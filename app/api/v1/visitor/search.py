from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.schemas.search import HostelSearchRequest, HostelSearchResponse, HostelSearchResult, HostelSearchFilters, HostelSearchSort
from app.services.search_service import SearchService

router = APIRouter(prefix="/visitor/search", tags=["Visitor Search"])

@router.post("/hostels", response_model=HostelSearchResponse)
def search_hostels(search_request: HostelSearchRequest, db: Session = Depends(get_db)):
    """Search hostels with filters and sorting (PostgreSQL or Elasticsearch)"""
    
    # Try Elasticsearch first for advanced features
    from app.core.elasticsearch import search_hostels_es, get_elasticsearch
    
    es_results = None
    if get_elasticsearch():
        try:
            filters_dict = search_request.filters.model_dump(exclude_none=True)
            es_results = search_hostels_es(
                query=filters_dict.get('query', ''),
                filters=filters_dict,
                size=search_request.page_size,
                from_=(search_request.page - 1) * search_request.page_size
            )
        except Exception as e:
            print(f"Elasticsearch search failed, falling back to PostgreSQL: {e}")
    
    if es_results:
        # Use Elasticsearch results
        results = []
        for hit in es_results['hits']:
            source = hit['_source']
            # Add distance if available
            if 'sort' in hit and len(hit['sort']) > 0:
                source['distance_km'] = hit['sort'][0]
            results.append(HostelSearchResult(**source))
        
        total_count = es_results['total']
        total_pages = (total_count + search_request.page_size - 1) // search_request.page_size
        
        response = HostelSearchResponse(
            results=results,
            total_count=total_count,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages
        )
        
        # Add facets/aggregations to response
        response.facets = es_results.get('aggregations', {})
        
    else:
        # Fallback to PostgreSQL
        hostels, total_count = SearchService.search_hostels(
            db, 
            search_request.filters, 
            search_request.sort,
            search_request.page,
            search_request.page_size
        )
        
        results = [HostelSearchResult(**hostel) for hostel in hostels]
        total_pages = (total_count + search_request.page_size - 1) // search_request.page_size
        
        response = HostelSearchResponse(
            results=results,
            total_count=total_count,
            page=search_request.page,
            page_size=search_request.page_size,
            total_pages=total_pages
        )
    
    # Log search for analytics
    SearchService.log_search(db, search_request.filters, total_count)
    
    return response

@router.get("/autocomplete")
def autocomplete_search(
    query: str = Query(..., min_length=2),
    field: str = Query("name", regex="^(name|location|city)$"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Autocomplete suggestions for hostel search"""
    from app.core.elasticsearch import autocomplete_hostels, get_elasticsearch
    
    if get_elasticsearch():
        suggestions = autocomplete_hostels(query, field, limit)
        if suggestions:
            return {"suggestions": suggestions}
    
    # Fallback to PostgreSQL LIKE search
    from sqlalchemy import text
    
    sql_query = f"""
        SELECT DISTINCT {field}, city
        FROM hostels
        WHERE LOWER({field}) LIKE LOWER(:query)
        LIMIT :limit
    """
    
    results = db.execute(
        text(sql_query),
        {'query': f'%{query}%', 'limit': limit}
    ).fetchall()
    
    return {
        "suggestions": [dict(row._mapping) for row in results]
    }

@router.get("/hostels/{hostel_id}")
def get_hostel_details(hostel_id: int, request: Request, db: Session = Depends(get_db)):
    """Get detailed hostel information"""
    from sqlalchemy import text
    
    hostel = db.execute(text("""
        SELECT * FROM hostels WHERE id = :id
    """), {'id': hostel_id}).first()
    
    if not hostel:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Hostel not found")
    
    # Log profile view
    visitor_ip = request.client.host if request.client else None
    SearchService.log_profile_view(db, hostel_id, source="direct", visitor_ip=visitor_ip)
    
    return dict(hostel._mapping)

@router.get("/cities")
def get_available_cities(db: Session = Depends(get_db)):
    """Get list of cities with available hostels"""
    from sqlalchemy import text
    # Use COALESCE to prefer hostels.city but fall back to locations.city
    # This ensures hostels seeded with a `location_id` are included
    cities = db.execute(text("""
        SELECT COALESCE(h.city, l.city) AS city, COUNT(*) AS hostel_count
        FROM hostels h
        LEFT JOIN locations l ON h.location_id = l.id
        WHERE COALESCE(h.city, l.city) IS NOT NULL
        GROUP BY COALESCE(h.city, l.city)
        ORDER BY city
    """)).fetchall()

    return [{"city": row.city, "hostel_count": row.hostel_count} for row in cities]

@router.get("/amenities")
def get_available_amenities(db: Session = Depends(get_db)):
    """Get list of all available amenities"""
    from sqlalchemy import text
    
    # Fetch amenities from hostels and split them
    amenities_list = set()
    rows = db.execute(text("""
        SELECT DISTINCT amenities
        FROM hostels
        WHERE amenities IS NOT NULL
        ORDER BY amenities
    """)).fetchall()
    
    for row in rows:
        if row.amenities:
            # Split by comma or other delimiters if stored as text
            items = [item.strip() for item in str(row.amenities).split(',')]
            amenities_list.update(items)
    
    return sorted(list(amenities_list))

@router.get("/facets")
def get_search_facets(db: Session = Depends(get_db)):
    """Get faceted search options (aggregations)"""
    from sqlalchemy import text
    
    # Get all facet data in one go
    facets = {
        "cities": [],
        "areas": [],
        "genders": [],
        "amenities": [],
        "price_ranges": {
            "under_5000": 0,
            "5000_10000": 0,
            "10000_15000": 0,
            "above_15000": 0
        }
    }
    
    # Cities
    cities = db.execute(text("""
        SELECT city, COUNT(*) as count
        FROM hostels WHERE city IS NOT NULL
        GROUP BY city ORDER BY count DESC
    """)).fetchall()
    facets["cities"] = [{"value": r.city, "count": r.count} for r in cities]
    
    # Genders
    genders = db.execute(text("""
        SELECT gender_type, COUNT(*) as count
        FROM hostels WHERE gender_type IS NOT NULL
        GROUP BY gender_type
    """)).fetchall()
    facets["genders"] = [{"value": r.gender_type, "count": r.count} for r in genders]
    
    # Amenities - extract from text field
    amenities_list = {}
    amenities_rows = db.execute(text("""
        SELECT amenities
        FROM hostels WHERE amenities IS NOT NULL
    """)).fetchall()
    
    for row in amenities_rows:
        if row.amenities:
            items = [item.strip() for item in str(row.amenities).split(',')]
            for item in items:
                amenities_list[item] = amenities_list.get(item, 0) + 1
    
    facets["amenities"] = [{"value": k, "count": v} for k, v in sorted(amenities_list.items(), key=lambda x: x[1], reverse=True)[:30]]
    
    # Remove price ranges and areas since they don't have columns
    facets.pop("price_ranges", None)
    facets.pop("areas", None)
    
    return facets
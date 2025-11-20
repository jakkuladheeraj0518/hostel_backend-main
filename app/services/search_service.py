from sqlalchemy.orm import Session
from sqlalchemy import text, and_, or_
from typing import List, Tuple
from app.schemas.search import HostelSearchFilters, HostelSearchSort, HostelSearchResult
import math

class SearchService:
    
    @staticmethod
    def search_hostels(db: Session, filters: HostelSearchFilters, 
                      sort: HostelSearchSort, page: int, page_size: int) -> Tuple[List[dict], int]:
        """Search hostels with filters and sorting"""
        
        # Use current schema: hostels has `hostel_name`, `full_address`, `total_beds`, `current_occupancy`,
        # and `location_id` referencing `locations.city`. There is no `name`, `location` or `is_active`.
        base_query = """
            SELECT h.id, h.hostel_name, h.description, h.full_address, l.city as city,
                   h.total_beds, h.current_occupancy, h.monthly_revenue, h.visibility,
                   h.contact_phone, h.contact_email, h.amenities, h.created_at
            FROM hostels h
            LEFT JOIN locations l ON l.id = h.location_id
            WHERE h.visibility = 'public'
        """
        
        params = {}
        
        # Apply filters
        conditions = []
        
        if filters.city:
            # city lives on the locations table
            conditions.append("LOWER(l.city) = LOWER(:city)")
            params['city'] = filters.city
        
        # area/pincode/gender/price/rating/geo are not present in current schema; apply what we can
        if filters.area:
            # no area column available — ignore or match against full_address
            conditions.append("LOWER(h.full_address) LIKE LOWER(:area)")
            params['area'] = f"%{filters.area}%"

        if filters.pincode:
            conditions.append("h.full_address LIKE :pincode")
            params['pincode'] = f"%{filters.pincode}%"

        if filters.gender:
            # no gender column defined on hostels; ignore filter
            pass

        if filters.min_price or filters.max_price:
            # price fields are not present; ignore price filtering
            pass

        if filters.min_rating:
            # rating is not present in current schema; ignore
            pass

        if filters.available_only:
            # available if total_beds > current_occupancy
            conditions.append("(h.total_beds IS NOT NULL AND COALESCE(h.current_occupancy, 0) < h.total_beds)")

        if filters.query:
            conditions.append(
                "(LOWER(h.hostel_name) LIKE LOWER(:query) OR LOWER(h.description) LIKE LOWER(:query) OR LOWER(h.full_address) LIKE LOWER(:query))"
            )
            params['query'] = f"%{filters.query}%"

        if filters.amenities:
            # amenities stored as TEXT; check substring match for each amenity
            for i, amenity in enumerate(filters.amenities):
                conditions.append(f"LOWER(h.amenities) LIKE LOWER(:amenity_{i})")
                params[f'amenity_{i}'] = f"%{amenity}%"
        
        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        # Sorting - limited options supported on current schema
        order_by = {
            'newest': 'h.created_at DESC',
            'distance': 'h.id ASC',
            'rating': 'h.id ASC'
        }
        sort_clause = order_by.get(sort.sort_by, 'h.created_at DESC')

        # Wrap with simple query and pagination
        query = f"""
            {base_query}
            ORDER BY {sort_clause}
            LIMIT :limit OFFSET :offset
        """

        # Count query
        count_query = f"SELECT COUNT(*) FROM ({base_query}) as sub"

        total_count = db.execute(text(count_query), params).scalar() or 0

        # Pagination
        offset = (page - 1) * page_size
        params['limit'] = page_size
        params['offset'] = offset

        # Execute query and map rows to expected result keys
        result = db.execute(text(query), params)
        hostels = []
        for row in result.fetchall():
            r = row._mapping
            total_beds = r.get('total_beds') or 0
            current_occupancy = r.get('current_occupancy') or 0
            available_beds = max(total_beds - current_occupancy, 0)
            amenities_raw = r.get('amenities') or ''
            amenities_list = [a.strip() for a in amenities_raw.split(',')] if isinstance(amenities_raw, str) and amenities_raw else []

            hostels.append({
                'id': r.get('id'),
                'name': r.get('hostel_name'),
                'description': r.get('description'),
                'location': r.get('full_address'),
                'city': r.get('city'),
                'area': None,
                'pincode': None,
                'latitude': None,
                'longitude': None,
                'gender': None,
                'contact_phone': r.get('contact_phone'),
                'contact_email': r.get('contact_email'),
                'available_beds': available_beds,
                'total_beds': total_beds,
                'price_range_min': None,
                'price_range_max': None,
                'rating': 0.0,
                'review_count': 0,
                'amenities': amenities_list,
                'photos': [],
                'distance_km': None
            })

        return hostels, int(total_count)
    
    @staticmethod
    def log_search(db: Session, filters: HostelSearchFilters, results_count: int):
        """Log search query for analytics"""
        from app.models.reports import SearchQuery
        import json
        from decimal import Decimal
        
        # Convert Decimal to float for JSON serialization
        filters_dict = filters.model_dump(exclude_none=True)
        for key, value in filters_dict.items():
            if isinstance(value, Decimal):
                filters_dict[key] = float(value)
        
        search_log = SearchQuery(
            query_text=filters.query or "",
            city=filters.city,
            filters=json.dumps(filters_dict),
            results_count=results_count
        )
        db.add(search_log)
        db.commit()
    
    @staticmethod
    def log_profile_view(db: Session, hostel_id: int, source: str = "direct", visitor_ip: str = None, session_id: str = None):
        """Log hostel profile view for analytics"""
        from app.models.reports import HostelProfileView
        
        view = HostelProfileView(
            hostel_id=hostel_id,
            source=source,
            visitor_ip=visitor_ip,
            session_id=session_id
        )
        db.add(view)
        db.commit()
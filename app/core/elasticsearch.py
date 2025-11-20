from elasticsearch import Elasticsearch
from app.config import settings
from typing import List, Dict, Any
import logging

# Suppress elasticsearch warnings
logging.getLogger('elastic_transport').setLevel(logging.ERROR)

es_client = None

def get_elasticsearch():
    global es_client
    if es_client is None:
        try:
            es_client = Elasticsearch(
                [settings.ELASTICSEARCH_URL],
                request_timeout=2,  # Faster timeout
                max_retries=0,  # Don't retry
                retry_on_timeout=False
            )
            # Quick ping to test connection
            if not es_client.ping():
                es_client = None
        except Exception as e:
            es_client = None
    return es_client

def init_elasticsearch_indices():
    """Initialize Elasticsearch indices for hostel search"""
    es = get_elasticsearch()
    if not es:
        print("Elasticsearch not available - search will use PostgreSQL")
        return
    
    try:
        index_name = "hostels"
        
        if not es.indices.exists(index=index_name):
            es.indices.create(
                index=index_name,
                body={
                    "settings": {
                        "analysis": {
                            "analyzer": {
                                "autocomplete_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "autocomplete_filter"]
                                },
                                "fuzzy_analyzer": {
                                    "type": "custom",
                                    "tokenizer": "standard",
                                    "filter": ["lowercase", "asciifolding"]
                                }
                            },
                            "filter": {
                                "autocomplete_filter": {
                                    "type": "edge_ngram",
                                    "min_gram": 2,
                                    "max_gram": 20
                                }
                            }
                        }
                    },
                    "mappings": {
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {
                                "type": "text",
                                "analyzer": "standard",
                                "fields": {
                                    "autocomplete": {
                                        "type": "text",
                                        "analyzer": "autocomplete_analyzer"
                                    },
                                    "fuzzy": {
                                        "type": "text",
                                        "analyzer": "fuzzy_analyzer"
                                    }
                                }
                            },
                            "description": {"type": "text"},
                            "location": {
                                "type": "text",
                                "fields": {
                                    "autocomplete": {
                                        "type": "text",
                                        "analyzer": "autocomplete_analyzer"
                                    }
                                }
                            },
                            "city": {"type": "keyword"},
                            "area": {"type": "keyword"},
                            "pincode": {"type": "keyword"},
                            "gender": {"type": "keyword"},
                            "price_range_min": {"type": "float"},
                            "price_range_max": {"type": "float"},
                            "rating": {"type": "float"},
                            "amenities": {"type": "keyword"},
                            "available_beds": {"type": "integer"},
                            "geo_location": {"type": "geo_point"}
                        }
                    }
                }
            )
        print("Elasticsearch indices initialized successfully")
    except Exception as e:
        print(f"Elasticsearch initialization failed: {e}")
        print("Application will continue without Elasticsearch - search will use PostgreSQL")

def index_hostel(hostel_data: Dict[str, Any]):
    """Index a single hostel to Elasticsearch"""
    es = get_elasticsearch()
    if not es:
        return False
    
    try:
        # Add geo_location point
        if hostel_data.get('latitude') and hostel_data.get('longitude'):
            hostel_data['geo_location'] = {
                'lat': float(hostel_data['latitude']),
                'lon': float(hostel_data['longitude'])
            }
        
        es.index(
            index="hostels",
            id=hostel_data['id'],
            body=hostel_data
        )
        return True
    except Exception as e:
        print(f"Error indexing hostel {hostel_data.get('id')}: {e}")
        return False

def bulk_index_hostels(hostels: List[Dict[str, Any]]):
    """Bulk index hostels to Elasticsearch"""
    es = get_elasticsearch()
    if not es:
        return False
    
    try:
        from elasticsearch.helpers import bulk
        
        actions = []
        for hostel in hostels:
            # Add geo_location point
            if hostel.get('latitude') and hostel.get('longitude'):
                hostel['geo_location'] = {
                    'lat': float(hostel['latitude']),
                    'lon': float(hostel['longitude'])
                }
            
            actions.append({
                '_index': 'hostels',
                '_id': hostel['id'],
                '_source': hostel
            })
        
        success, failed = bulk(es, actions)
        print(f"Elasticsearch bulk index: {success} successful, {len(failed)} failed")
        return True
    except Exception as e:
        print(f"Error bulk indexing hostels: {e}")
        return False

def search_hostels_es(query: str, filters: Dict[str, Any], size: int = 20, from_: int = 0):
    """Advanced search using Elasticsearch"""
    es = get_elasticsearch()
    if not es:
        return None
    
    try:
        # Build Elasticsearch query
        must_conditions = []
        filter_conditions = []
        
        # Full-text search with fuzzy matching
        if query:
            must_conditions.append({
                "multi_match": {
                    "query": query,
                    "fields": ["name^3", "name.fuzzy^2", "description", "location.autocomplete"],
                    "fuzziness": "AUTO",
                    "prefix_length": 1
                }
            })
        
        # Filters
        if filters.get('city'):
            filter_conditions.append({"term": {"city": filters['city']}})
        
        if filters.get('area'):
            filter_conditions.append({"term": {"area": filters['area']}})
        
        if filters.get('gender'):
            filter_conditions.append({"term": {"gender": filters['gender']}})
        
        if filters.get('amenities'):
            for amenity in filters['amenities']:
                filter_conditions.append({"term": {"amenities": amenity}})
        
        # Price range
        if filters.get('min_price') or filters.get('max_price'):
            price_range = {}
            if filters.get('min_price'):
                price_range['gte'] = filters['min_price']
            if filters.get('max_price'):
                price_range['lte'] = filters['max_price']
            filter_conditions.append({"range": {"price_range_min": price_range}})
        
        # Rating
        if filters.get('min_rating'):
            filter_conditions.append({"range": {"rating": {"gte": filters['min_rating']}}})
        
        # Availability
        if filters.get('available_only'):
            filter_conditions.append({"range": {"available_beds": {"gt": 0}}})
        
        # Geo distance filter
        if filters.get('latitude') and filters.get('longitude'):
            filter_conditions.append({
                "geo_distance": {
                    "distance": f"{filters.get('radius_km', 5)}km",
                    "geo_location": {
                        "lat": filters['latitude'],
                        "lon": filters['longitude']
                    }
                }
            })
        
        # Build final query
        es_query = {
            "query": {
                "bool": {
                    "must": must_conditions if must_conditions else [{"match_all": {}}],
                    "filter": filter_conditions
                }
            },
            "size": size,
            "from": from_
        }
        
        # Add geo distance sorting if coordinates provided
        if filters.get('latitude') and filters.get('longitude'):
            es_query["sort"] = [
                {
                    "_geo_distance": {
                        "geo_location": {
                            "lat": filters['latitude'],
                            "lon": filters['longitude']
                        },
                        "order": "asc",
                        "unit": "km"
                    }
                }
            ]
        
        # Add aggregations for faceted search
        es_query["aggs"] = {
            "cities": {"terms": {"field": "city", "size": 50}},
            "areas": {"terms": {"field": "area", "size": 50}},
            "genders": {"terms": {"field": "gender"}},
            "amenities": {"terms": {"field": "amenities", "size": 50}},
            "price_ranges": {
                "range": {
                    "field": "price_range_min",
                    "ranges": [
                        {"to": 5000},
                        {"from": 5000, "to": 10000},
                        {"from": 10000, "to": 15000},
                        {"from": 15000}
                    ]
                }
            }
        }
        
        response = es.search(index="hostels", body=es_query)
        
        return {
            "hits": response['hits']['hits'],
            "total": response['hits']['total']['value'],
            "aggregations": response.get('aggregations', {})
        }
    except Exception as e:
        print(f"Elasticsearch search error: {e}")
        return None

def autocomplete_hostels(query: str, field: str = "name", size: int = 10):
    """Autocomplete suggestions for hostel search"""
    es = get_elasticsearch()
    if not es:
        return []
    
    try:
        response = es.search(
            index="hostels",
            body={
                "query": {
                    "match": {
                        f"{field}.autocomplete": {
                            "query": query,
                            "operator": "and"
                        }
                    }
                },
                "size": size,
                "_source": [field, "city", "area"]
            }
        )
        
        return [hit['_source'] for hit in response['hits']['hits']]
    except Exception as e:
        print(f"Autocomplete error: {e}")
        return []
from datetime import datetime
import urllib.parse
import motor.motor_asyncio
import json
from bson.json_util import dumps as bson_dumps
from .model import *
from .config import host, username, password

username = urllib.parse.quote_plus(username)
password = urllib.parse.quote_plus(password)
## 主機
mongodb_url = f"mongodb://{username}:{password}@{host}/capt_logs?retryWrites=true&w=majority"
## 訓練機
# mongodb_url = f"mongodb://{username}:{password}@{host}/?authMechanism=DEFAULT&authSource=capt_logs"
client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_url)

async def query_capt_logs(query: Query):
    try:
        await client.server_info()
    except Exception:
        print("Unable to connect to the server.")
    db = client[query.db_name]
    collection = db[query.collection_name]
    start_date = None
    end_date = None
    find_filter = {"source": {"$in": query.where.source}}
    
    if query.where.created_at:
        start_date = datetime.strptime(query.where.created_at.start_date, "%Y-%m-%d %H:%M:%S") if query.where.created_at.start_date else None

        if query.where.created_at.end_date:
            end_date = datetime.strptime(query.where.created_at.end_date, "%Y-%m-%d %H:%M:%S")
        else:
            end_date = datetime.now()

    if query.where.id:
        find_filter["id"] = {"$in": query.where.id}

    if query.where.user_id:
        find_filter["user_id"] = {"$in": query.where.user_id}

    if query.where.sentence:
        find_filter["sentence"] = {"$regex": f".*{query.where.sentence}.*"}
    
    if query.where.source_id:
        find_filter["source_id"] = {"$in": query.where.source_id}
        
    if query.where.gop:
        find_filter["gop"] = {"$gte": query.where.gop.gte, "$lte": query.where.gop.lte}
        
    if start_date and end_date:
        find_filter["created_at"] = {"$gte": start_date, "$lte": end_date}

    total_matched_records = await collection.count_documents(find_filter)

    if query.select == "count(*)":
        count = await collection.count_documents(find_filter)
        return {"count": count}

    elif isinstance(query.select, DistinctAggregation):
            pipeline = [
                {"$match": find_filter},
                {"$group": {"_id": {field: f"${field}" for field in query.select.field_names}}},
                {"$project": {"_id": 0, **{f"{field}": f"$_id.{field}" for field in query.select.field_names}}}
            ]
            
            pipeline.extend([
                {"$skip": query.skip},
                {"$limit": query.limit}
            ])
            
            cursor = collection.aggregate(pipeline)
            result = await cursor.to_list(length=None)
            json_content = {"total_matched_records": total_matched_records, "results": json.loads(bson_dumps(list(result)))}
            return json_content
    
    elif isinstance(query.select[0], Aggregation):
        pipeline = [
            {"$match": find_filter},
            {"$skip": query.skip},
            {"$limit": query.limit} if query.limit != 0 else None
        ]
        pipeline = list(filter(None, pipeline))
        agg_dict = {"_id": None}
        for select in query.select:
            agg_dict[select.field] = {f"${select.op}": f"${select.field}"}
        
        pipeline.append({"$group": agg_dict})
        pipeline.append({"$project": {"_id": 0}})
        
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        json_content = {"total_matched_records": total_matched_records, "results": json.loads(bson_dumps(result))}
        return json_content

    else:
        cursor = collection.find(
            find_filter,
            {**{key: 1 for key in query.select}, "_id": 0}
        )
        if query.sort:
            cursor = cursor.sort(query.sort.field, query.sort.order)

        cursor = cursor.skip(query.skip).limit(query.limit)
        documents = await cursor.to_list(length=None)
        # async for document in cursor:
        #     pprint(document)
        # for document in documents:
        #     pprint(document)
        for document in documents:
            if "created_at" in document:
                document["created_at"] = document["created_at"].strftime("%Y-%m-%d %H:%M:%S")                        
        return documents

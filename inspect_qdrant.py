import qdrant_client
c = qdrant_client.QdrantClient(location=":memory:")
print("Methods containing 'search':")
print([x for x in dir(c) if "search" in x])
print("Methods containing 'query':")
print([x for x in dir(c) if "query" in x])

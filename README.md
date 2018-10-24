# computer-network

## udp_s: Local DNS Resolver
### Function
Using socket to answer dns query, if query exist in local cache, deal with TTL then return to client, If query not exist in cache, pass the query to upstrem DNS server and add it to cache then pass the response data to client.

# -*- coding: UTF-8 -*-
from socket import *
import time
import struct
cache =[]
DNSserver = '8.8.8.8'   
# A                1，主机地址 
# NS               2，权威名称服务器 
# CNAME            5，别名的正则名称 
# MX               15，邮件交换
# TXT              16，文本字符串
# AAAA	           28，ipv6 地址    
# sent to upstream DNS server or get from cache
def DNSSocket(message):
    # make transaction id the same as query
    id  = message[0:2]
    # use queryName for a identifier for cache
    queryName = message[12:]
    # look through cache
    for i in cache:
        # if hit query in cache and ttl satisfied, get from cache
        if queryName == i['queryName'] and i['recvTime']+i['TTL'] > time.time():
            # print('cache')
            res = id + i['dnsResponse'][2:]
            dnsRes = res
            AnswerNum = struct.unpack(">H",dnsRes[6:8])[0]
            count = 12
            questionNum = struct.unpack(">H",dnsRes[4:6])[0]
            # print('questionNum',questionNum)
            # for loop of question
            for j in range(0,questionNum):
                while(dnsRes[count]!=0):
                    # print(dnsRes[count])
                    labelLen = dnsRes[count]+1
                    count += labelLen
                    # print('question count:',count)
                count += 4
                # print('count1:',count)
            # answer res
            # for loop of answer
            for j in range(0,AnswerNum):
                # print('dns')
                # print(dnsRes[count+7:count+11])
                a = struct.unpack(">I",dnsRes[count+7:count+11])[0]
                b = int(i['recvTime'] + a - time.time())
                b = struct.pack(">L",b)
                # print('b',b)
                dnsRes = dnsRes[:count+7]+ b + dnsRes[count+11:]
                began = count+11
                end = count+13
                # print('count2',count)
                datalen = struct.unpack(">H",dnsRes[began:end])[0]
                # print('datalen',datalen)
                count = 12 + datalen + count
            return dnsRes
    # make a socket to upstream dns server
    ClientSocket = socket(AF_INET, SOCK_DGRAM)
    # sent message get from client directly to dns server. 
    ClientSocket.sendto(message, (DNSserver,53))
    dnsRes,addr = ClientSocket.recvfrom(2048)
    # print(dnsRes)
    # add result to cache
    temp ={}
    temp['queryName'] = queryName
    temp['dnsResponse'] = dnsRes
    temp['recvTime'] = time.time()
    AnswerNum = struct.unpack(">H",dnsRes[6:8])[0]
    count = 12
    TTL = 100000000
    questionNum = struct.unpack(">H",dnsRes[4:6])[0]
    # print('questionNum',questionNum)
    for j in range(0,questionNum):
        while(dnsRes[count]!=0):
            # print(dnsRes[count])
            labelLen = dnsRes[count]+1
            count += labelLen
            # print('question count:',count)
        count += 4
        # print('count1:',count)
    # answer res
    for j in range(0,AnswerNum):
        # print('dns')
        a = struct.unpack(">I",dnsRes[count+7:count+11])[0]
        # print('ttl:',a)
        if a < TTL:
            TTL = a
        began = count+11
        end = count+13
        # print('count2',count)
        datalen = struct.unpack(">H",dnsRes[began:end])[0]
        # print("datalen")
        # print(datalen)
        count = 12 + datalen + count
    temp['TTL']=TTL
    cache.append(temp)
    # print('ans',AnswerNum)
    # print(cache)
    # print('query from DNS server', DNSserver)

    return dnsRes

def ClientSocket():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', 53))
    print("The server is ready to receive")
    while True:
        message, (clientAddress,clientPort) = serverSocket.recvfrom(2048)
        # print('the message list is:',list(message))
        # invoke DNSSocket()
        message= DNSSocket(message)
        serverSocket.sendto(message, (clientAddress,clientPort))
# as client end to query dns information from DNS server such as 8.8.8.8



if __name__=="__main__":
    ClientSocket()

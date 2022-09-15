cd app/client
../dana/dnc . -v
cd ../readn
../dana/dnc . -v
cd ../readn-writen
../dana/dnc . -v
cd ../writen
../dana/dnc . -v
cd ../server
../dana/dnc . -v
cd ../distributor
../dana/dnc . -sp ../server -v
cd ..
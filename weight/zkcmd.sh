source setenv.sh
zkServer.sh $1 zoo_1.cfg
sleep 2
zkServer.sh $1 zoo_2.cfg
sleep 2
zkServer.sh $1 zoo_3.cfg
sleep 2
zkServer.sh $1 zoo_4.cfg
sleep 2

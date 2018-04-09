#!/usr/bin/expect -f

#trap sigwinch and pass it to the child we spawned
trap {
 set rows [stty rows]
 set cols [stty columns]
 stty rows $rows columns $cols < $spawn_out(slave,name)
} WINCH

set timeout 20
spawn ssh xcwang@127.0.0.1 -p 7022 -Y
expect "password:"
send "000000\r"

interact


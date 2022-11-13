#!/bin/bash
# version 1.0.2

request_user() {
request=0
counter=0
out=0
echo "---------------------------"
echo "- Select destination [0]: -"
echo "-             stage = 1   -"
echo "-              prod = 2   -"
echo "-       exit sctipt = 0   -"
echo "---------------------------"

while ISF= read -s -t 10 -n 1 request
do
 counter=$((counter+1))
 if [ $counter -gt 10 ]
  then
   echo Are You Stupid?
   request=0
 fi 
 request=${request:-0}

 re='^[0-9]+$'
 if ! [[ $request =~ $re ]] ; then
    echo "ERROR NOT NUMBER"
    request=11
 fi 
# echo $request
 if [ $request -eq 0 ]
  then
   echo 
   echo -n Exit!
   exit 0
 fi
 if [ $request -eq 1 ] || [ $request -eq 2 ]
  then 
   echo Selected: $request
   if [ $request -eq 2 ]
    then
    echo that''s PRODUCTION
    else
    echo that''s STAGES
   fi
   echo -----------------
   echo "are you sure?(Y/N) [N]"
   char=N
   read -p "Enter symbol and press [ENTER]:" char
   if [ "$char" == "Y" ] || [ "$char"  == "y" ]; then
   echo 
   echo -e "GO!"
   export out=$request
    break
   else
    echo Exit!
    exit 0
   fi
 fi
done
}

# Begin
request_user;

# End
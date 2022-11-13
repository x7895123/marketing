#!/bin/bash

# v1.0.3
################################################################
# Now enable argument, for silent mode
# $1 - 1 or 2 or .... -  Select destination ...
################################################################


check_variable() {
    error="ERROR"
    case $out in
      "1"|"2") error=""; ;;
       *) error="ERROR OUT"; ;;
    esac

    size=${#nver}
    if [ "$size" -lt 5 ]; then
        error="ERROR NVER SIZE"
    fi

    size=`echo $nver | grep -o "\." | grep -c "\."`
    if [ "$size" -ne 2 ]; then
        error="ERROR NVER FORMAT"
    fi

    size=${#dver}
    if [ "$size" -ne 10 ]; then
        error="ERROR DVER SIZE"
    fi

    re='^[0-9]+$'
    if ! [[ $dver =~ $re ]] ; then
       error="ERROR NOT NUMBER"
    fi

    re='^[a-z]+$'
    if ! [[ $srv =~ $re ]] ; then
       error="ERROR NAME"
    fi
    echo $error
}


# begin
if [ -n "$1" ]; then
    out=$1
else
    . ./request.sh
fi

if [ -z "$out" ]; then
    echo No selected.
    exit 0 
fi

case $out in
    "1") repobrantch=stage-dostyq; ;;
    "2") repobrantch=prod-dostyq; ;;
    *) echo ERROR ARGUMENT; exit 0; ;;
esac

repo="images.chicago.loc/"$repobrantch
prefix="server-"
srv=`cat VERSION |grep servicename|sed 's/servicename="//'|sed 's/"//'`
nver=`cat VERSION |grep version|sed 's/version="//'|sed 's/"//'`
dver=`cat VERSION |grep date|sed 's/date="//'|sed 's/"//'|sed -E 's/-//g'`
fname=$repo':'$srv'-'$nver'-'$dver

echo "Name service     :"$prefix$srv
echo "Version          :"$nver
echo "Version-release  :"$dver
echo "Image repo       :"$repobrantch
echo "Full image name  :"$fname

check_variable;

if [ -n "$error" ]; then
    echo Exit ERROR!
    exit 0
fi

echo Start build ...
docker build -f Dockerfile -t $fname  --build-arg version='"'$nver'"'  --build-arg date='"'$dver'"' .
docker push $fname
docker images $fname
# end

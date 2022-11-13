#!/bin/bash
# v1.0.3
################################################################
# Now enable two arguments, for silent mode
# $1 - 1 or 2 or .... -  Select destination ...
# $2 - F or N - Force DEPLOY without request or force NO DEPLOY(only generate YAML) 
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
    "1") repobrantch=stage-dostyq;branch=stage;nspace=dostyk; ;;
    "2") repobrantch=prod-dostyq;branch=prod;nspace=prod-dostyq; ;;
    *) echo ERROR ARGUMENT; exit 0; ;;
esac

case $2 in
    "F"|"f") force=1; ;;
    "N"|"n") force=0; ;;
    *) force=""; ;;
esac

repo="images.chicago.loc\/"$repobrantch
prefix="server-"
srv=`cat VERSION |grep servicename|sed 's/servicename="//'|sed 's/"//'`
nver=`cat VERSION |grep version|sed 's/version="//'|sed 's/"//'`
dver=`cat VERSION |grep date|sed 's/date="//'|sed 's/"//'|sed -E 's/-//g'`
fname=$repo':'$srv'-'$nver'-'$dver

echo "Name service     :"$prefix$srv
echo "Version          :"$nver
echo "Version-release  :"$dver
echo "Namespace        :"$nspace
echo "Branch           :"$branch
echo "Image repo       :"$repobrantch
echo "Full image name  :"$fname

check_variable;

if [ -n "$error" ]; then
    echo Exit ERROR!
    exit 0
fi

echo Start bild YAML ...
cat yaml/overload/$branch/custversion.tmpl | sed "s/PPPPPP/$fname/g"  | sed "s/YYYYYY/$nver-$dver/g" > yaml/overload/$branch/custversion.yaml \
&& kubectl kustomize ./yaml/overload/$branch/ >deploy.yaml \
&& sed -i -e "s/SSSSSS/$prefix$srv/g" deploy.yaml\
&& kubectl  apply --dry-run=client --validate -f deploy.yaml \
&& rm -f yaml/overload/$branch/custversion.yaml 

if [ -z "$force" ]; then
    echo -----------------
    echo "Deploy now?(Y/N) [N]"
    char=N
    read -p "Enter symbol and press [ENTER]:" char
    if [ "$char" == "Y" ] || [ "$char"  == "y" ]; then
        force=1
    else
        echo Exit!
        exit 0
   fi
fi

if [ "$force" -eq 0 ]; then
    exit 0
fi

echo -e "- Start deploy -"

kubectl -n $nspace apply -f deploy.yaml
kubectl -n $nspace get pod -o wide | grep server-$srv
status=0
x=1
echo Stoping ...
while [ $x -le 60 ]
do
    sleep 3
    x=$(( $x + 1 ))
    status=`kubectl -n $nspace get pod |grep server-$srv |awk '{print $3}'`
    echo $status
    if  [ $x -eq 59 ]; then
     echo Stoping ERROR!
     exit 1
    fi
    if  [ "$status" == "" ]; then
     x=100
    fi
done

kubectl scale -n $nspace deployment server-$srv --replicas=1
x=1
echo Starting ...
while [ $x -le 60 ]
do
    sleep 3
    x=$(( $x + 1 ))
    status=`kubectl -n $nspace get pod |grep server-$srv |awk '{print $3}'`
    echo $status
    if  [ $x -eq 59 ]; then
     echo Starting ERROR!
     exit 1
    fi
    if  [ "$status" == "Running" ]; then
     x=100
    fi
done

kubectl -n $nspace get pod -o wide | grep server-$srv
# end
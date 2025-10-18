#!/bin/bash
# 备份palword
palPath=/home/steam/.local/share/Steam/steamapps/common/PalServer/Pal/Saved
backupPath=/home/steam/palbackup

backup () {
if [ ! -d $palPath ]; then
    echo "$palPath not exist"
    exit 1
fi

if [ ! -d $backupPath ]; then
    mkdir -p $backupPath
fi

backup_time=$(date +%Y%m%d_%H%M%S)
backup_filename=${backup_time}-palserver.tgz

cd $palPath/../
tar zcvf $backup_filename Saved 
mv $backup_filename $backupPath

echo "backup game saved to ${backupPath}/${backup_filename}"
}


while getopts ":s:t:" opt; 
    do
    case $opt in
    s)
        palPath=$OPTARG
        ;;
    t)
        backupPath=$OPTARG
        ;;
    :)
        echo "-$OPTARG 需要参数值"
        exit 1
        ;;
    ?)
        echo "-$OPTARG 参数错误"
        exit 1
        ;;
    esac
done
echo $palPath
echo $backupPath
backup
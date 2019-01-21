#!/usr/bin/env bash

HELP="\nEntre com o arquivo CSV como parametro.\n"
function help () {
	[ -n "$1" ] && HELP=$1
	echo -e "$HELP"
	exit 9
}

if [[ -r $1 ]]; then
  ### Cria o arquivo de saida: entrada.all
  ALLFILE="${1%%.*}.all"
	echo -n "" > $ALLFILE
  count=0
  #exec 3<&0 # necessario pra funcionar o read dentro do while
  #cat $1 | cut -d',' -f1,3 | sed 's/\"//g' | awk 'NR>1' | \
  ### Pega o primeiro e terceiro campo do CSV
  cat $1 | cut -d',' -f1,3 | sed 's/\"//g' | \
  while read line ; do
    ((count++))
    ### Filtra os HP e Offline:
    if [[ -z "$(echo $line | cut -d',' -f2)" ]]; then
      sed -n "$count"p $1 | grep -q "Contact Lost" && \
          echo "$line""Contact_Lost" >> $ALLFILE
      sed -n "$((count+1))"p $1 | grep -q "Hewlett Packard" && \
        echo "$line""HP" >> $ALLFILE
    else
      [[ "$(echo $line | cut -d',' -f1)" =~ \
          ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]] && \
              echo $line >> $ALLFILE
    fi
  done
  ### Separar Enterasys, Extreme e outros
  RESTO="${1%%.*}.outros" ; cat "$ALLFILE" > "$RESTO.tmp"
  ENFILE="${1%%.*}.en"
  EXFILE="${1%%.*}.ex"
  grep [A-C][1-9] "$ALLFILE" | cut -d',' -f1 > $ENFILE
  grep -v [A-C][1-9] "$RESTO.tmp" | tee "$RESTO" > /dev/null
  cat "$RESTO" > "$RESTO.tmp"
  grep X[1-9] "$ALLFILE" | cut -d',' -f1  > "$EXFILE"
  grep -v X[1-9] "$RESTO.tmp" | tee "$RESTO" > /dev/null
  rm "$RESTO.tmp"
  # ./ent.py "$ENFILE"
  # ./ext.py "$EXFILE"
else
  help
fi

exit 0


function mod() {
  ### Mostrar o modelos dos que falharam
  [[ -z $1 ]] && help "mod precisa de arquivo como parametro"
  echo -n "" "$1.model"
  for i in `cat $1`; do
    grep $i $ALLFILE >> "$1.model"
  done
}

case $1 in
  "raw") $1 $2 ;;
  "mod") $1 $2 ;;
  *) help ;;
esac

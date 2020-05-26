#! env sh
for sgf in `ls sgf`;
do
  tr < ./sgf/${sgf} -d '\000' > ./NoNull000/${sgf}
  tr < ./sgf/${sgf} -d '\x00' > ./NoNullx00/${sgf}
done

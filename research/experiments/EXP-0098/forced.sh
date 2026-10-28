set -eo pipefail
R=local/mednafen/agent/runs
for spec in "bison f00009560 060F9ED6" "akuma f00013840 060F9E16"; do
  set -- $spec
  for i in $(seq 0 15); do
    n=$(printf %02d $i)
    [ -f $R/re050-$1-r$n/capture.json ] && continue
    ./invenv.sh python -c "from tools.mednafen.agent import Agent; Agent().run()" || true
    ./invenv.sh python -m tools.mednafen.ko_capture --state local/re050/play/rec/states/$2.mcs \
      --out-dir $R/re050-$1-r$n --force-index $i --setter-pcs 060AF282 --quote-state $3 \
      --timeout 200 > $R/re050-$1-r$n.log 2>&1
    echo "$1 r$n done"
  done
done
./invenv.sh python -m tools.mednafen.verify_records --compile-dir build/ref012_m8_roster_gold_us \
  --out local/re050/verify.json $R/re050-bison-r?? $R/re050-akuma-r?? | tail -20

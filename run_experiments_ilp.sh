#!/bin/bash

INSTANCES=(
    "tsiligirides_problem_1_budget_80"
    "tsiligirides_problem_1_budget_50"
    "tsiligirides_problem_2_budget_25"
    "tsiligirides_problem_2_budget_40"
    "tsiligirides_problem_3_budget_070"
    "tsiligirides_problem_3_budget_100"
    "set_66_1_120"
    "set_66_1_070"
    "cemb_300_150"
    "cemb_300_250"
    "cemb_300_450"
    "cemb_150_140"
    "cemb_150_230"
    "cemb_150_290"
)

MAX_TIME=600
FIGURE_EXPORT_OPTION=2
BASE_OUT_DIR="results"

for INSTANCE in "${INSTANCES[@]}"; do
    echo "----------------------------------------"
    echo "Running instance: $INSTANCE"
    echo "----------------------------------------"

    for CONFIG in 1; do
        echo "▶ Execution $CONFIG"

        case $CONFIG in
            1)
                CONFIG_NAME="ilp"
                ;;
        esac

        OUT_DIR="${BASE_OUT_DIR}/${INSTANCE}/${CONFIG_NAME}"

        PLOT_SCORE="--plot_score"
        if [[ $INSTANCE == cemb* ]]; then
            PLOT_SCORE=""
        fi
        
        python -m src.run_ilp \
            --instance "$INSTANCE" \
            --out "$OUT_DIR" \
            --max_time "$MAX_TIME" \
            --figure_export_option "$FIGURE_EXPORT_OPTION" \
            --config_name "$CONFIG_NAME" \
            $PLOT_SCORE

        echo "✅ Finished: $INSTANCE (setting $CONFIG)"
        echo
    done

    echo "----------------------------------------"
    echo "✅ Finished all executions for instance: $INSTANCE"
    echo "----------------------------------------"
    echo
done

echo "🚀 All instances was executed with success!"

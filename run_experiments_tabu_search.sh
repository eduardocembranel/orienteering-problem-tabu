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

TARGETS=(
    "280"
    "190"
    "230"
    "395"
    "640"
    "800"
    "1645"
    "1120"
    "450"
    "1020"
    "2285"
    "1610"
    "2540"
    "3035"
)

MAX_TIME=600
FIGURE_EXPORT_OPTION=2
EXPORT_FIGURE_LEVEL=0
RNG=0
BASE_OUT_DIR="results"

for i in "${!INSTANCES[@]}"; do
    INSTANCE="${INSTANCES[$i]}"
    TARGET="${TARGETS[$i]}"

    echo "----------------------------------------"
    echo "Running instance: $INSTANCE"
    echo "----------------------------------------"

    for CONFIG in 1 2 3; do
        echo "▶ Execution $CONFIG"

        case $CONFIG in
            1)
                CONFIG_NAME="tabu"
                IMPROVE_FLAG="--first_improve"
                EXTRA_ARGS=""
                ;;
            2)
                CONFIG_NAME="tabu-div"
                IMPROVE_FLAG="--first_improve"
                EXTRA_ARGS="--diversification"
                ;;
            3)
                CONFIG_NAME="tabu-int"
                IMPROVE_FLAG="--first_improve"
                EXTRA_ARGS="--intensification"
                ;;
        esac

        PLOT_SCORE="--plot_score"
        if [[ $INSTANCE == cemb* ]]; then
            PLOT_SCORE=""
        fi

        OUT_DIR="${BASE_OUT_DIR}/${INSTANCE}/${CONFIG_NAME}"
        python -m src.run_tabu_search \
            --instance "$INSTANCE" \
            --out "$OUT_DIR" \
            --max_time "$MAX_TIME" \
            --target "$TARGET" \
            --figure_export_option "$FIGURE_EXPORT_OPTION" \
            --export_figure_level "$EXPORT_FIGURE_LEVEL" \
            --config_name "$CONFIG_NAME" \
            $IMPROVE_FLAG \
            $EXTRA_ARGS \
            $PLOT_SCORE \
            --rng "$RNG"

        echo "✅ Finished: $INSTANCE (setting $CONFIG)"
        echo
    done

    echo "----------------------------------------"
    echo "✅ Finished all executions for instance: $INSTANCE"
    echo "----------------------------------------"
    echo
done

echo "🚀 All instances was executed with success!"

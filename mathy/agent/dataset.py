from pathlib import Path

import numpy
import tensorflow as tf
import ujson

from ..agent.features import (
    FEATURE_BWD_VECTORS,
    FEATURE_FWD_VECTORS,
    FEATURE_LAST_BWD_VECTORS,
    FEATURE_LAST_FWD_VECTORS,
    FEATURE_LAST_RULE,
    FEATURE_MOVE_COUNTER,
    FEATURE_MOVES_REMAINING,
    FEATURE_NODE_COUNT,
    FEATURE_MOVE_MASK,
    FEATURE_PROBLEM_TYPE,
    TRAIN_LABELS_TARGET_NODE_CONTROL,
    TRAIN_LABELS_TARGET_GROUPING_CONTROL,
    TRAIN_LABELS_TARGET_GROUP_PREDICTION,
    TRAIN_LABELS_TARGET_REWARD_PREDICTION,
    TRAIN_LABELS_TARGET_PI,
    TRAIN_LABELS_TARGET_VALUE,
    parse_example_for_training,
)
from ..environment_state import INPUT_EXAMPLES_FILE_NAME


def make_training_input_fn(examples, batch_size):
    """Return an input function that lazily loads self-play examples from 
    the given file during training
    """

    output_types = (
        {
            FEATURE_FWD_VECTORS: tf.int64,
            FEATURE_BWD_VECTORS: tf.int64,
            FEATURE_LAST_FWD_VECTORS: tf.int64,
            FEATURE_LAST_BWD_VECTORS: tf.int64,
            FEATURE_LAST_RULE: tf.int64,
            FEATURE_NODE_COUNT: tf.int64,
            FEATURE_MOVE_COUNTER: tf.int64,
            FEATURE_MOVES_REMAINING: tf.int64,
            FEATURE_PROBLEM_TYPE: tf.int64,
            FEATURE_MOVE_MASK: tf.int64,
        },
        {
            TRAIN_LABELS_TARGET_PI: tf.float32,
            TRAIN_LABELS_TARGET_NODE_CONTROL: tf.int32,
            TRAIN_LABELS_TARGET_GROUPING_CONTROL: tf.int32,
            TRAIN_LABELS_TARGET_GROUP_PREDICTION: tf.int32,
            TRAIN_LABELS_TARGET_REWARD_PREDICTION: tf.int32,
            TRAIN_LABELS_TARGET_VALUE: tf.float32,
        },
    )

    lengths = [len(l["features"][FEATURE_BWD_VECTORS]) for l in examples]
    pi_lengths = [len(numpy.array(l["policy"]).flatten()) for l in examples]

    max_sequence = max(lengths)
    max_pi_sequence = max(pi_lengths)

    def _lazy_examples():
        nonlocal max_sequence
        for ex in examples:
            yield parse_example_for_training(ex, max_sequence, max_pi_sequence)

    def _input_fn():
        nonlocal output_types

        dataset = tf.data.Dataset.from_generator(
            _lazy_examples, output_types=output_types
        )
        # Shuffled during long-term memory extraction
        # dataset = dataset.shuffle(50000)
        dataset = dataset.repeat()
        dataset = dataset.batch(batch_size=batch_size)
        return dataset

    return _input_fn

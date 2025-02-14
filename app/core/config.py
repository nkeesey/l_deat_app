import dash_bootstrap_components as dbc

class Config:
    SECRET_KEY = 'dev'
    DEBUG = True
    STYLESHEET = dbc.themes.BOOTSTRAP
    MAX_ROWS = 11000

    # Feature lists
    EXPERIMENTAL_FEATURES = [
    'p_reward_sum_mean',
    'p_reward_sum_std',
    'p_reward_sum_median',
    'p_reward_contrast_mean',
    'p_reware_contrast_median',
    'reward_volume_left_mean',
    'reward_volume_right_mean',
    'effective_block_length_mean',
    'effective_block_length_std',
    'effective_block_length_median',
    'effective_block_length_min',
    'effective_block_length_max',
    'duration_gocue_stop_mean',
    'duration_gocue_stop_std',
    'duration_gocue_stop_median',
    'duration_gocue_stop_min',
    'duration_gocue_stop_max',
    'duration_delay_period_mean',
    'duration_delay_period_std',
    'duration_delay_period_median',
    'duration_delay_period_min',
    'duration_delay_period_max',
    'duration_iti_mean',
    'duration_iti_std',
    'duration_iti_median',
    'duration_iti_min',
    'duration_iti_max'
]

    PERFORMANCE_FEATURES = [
        'total_trials_with_autowater',
        'finished_trials_with_autowater',
        'finished_rate_with_autowater',
        'ignore_rate_with_autowater',
        'autowater_collected',
        'autowater_ignored',
        'total_trials',
        'finished_trials',
        'ignored_trials',
        'finished_rate',
        'ignore_rate',
        'reward_trials',
        'reward_rate',
        'foraging_eff',
        'foraging_eff_random_seed',
        'foraging_performance',
        'foraging_performance_random_seed',
        'bias_naive',
        'early_lick_rate',
        'invalid_lick_ratio',
        'double_dipping_rate_finished_trials',
        'double_dipping_rate_finished_reward_trials',
        'double_dipping_rate_finished_noreward_trials',
        'lick_consistency_mean_finished_trials',
        'lick_consistency_mean_finished_reward_trials',
        'lick_consistency_mean_finished_noreward_trials',
        'reaction_time_median',
        'reaction_time_mean'
    ]
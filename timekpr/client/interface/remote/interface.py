import requests


class timekprRemoteBus:
    def __init__(self, remote_host, remote_access_token):
        self.remote_host = remote_host
        self.remote_access_token = remote_access_token

    def getHostList(self):
        host_list = requests.get(
            self.remote_host + "/available_hosts", headers={"Authorization": f"Bearer {self.remote_access_token}"}
        )
        host_list = host_list.json()
        return host_list

    def getUserList(self):
        pass

    def getUserInformation(self, user_name, info_lvl):
        pass

    def setAllowedDays(self, user_name, day_list):
        pass

    def setAllowedHours(self, user_name, day_number, hour_list):
        pass

    def setTimeLimitForDays(self, user_name, day_limits):
        pass

    def setTimeLimitForWeek(self, user_name, time_limit_week):
        pass

    def setTimeLimitForMonth(self, user_name, time_limit_month):
        pass

    def setTrackInactive(self, user_name, track_inactive):
        pass

    def setHideTrayIcon(self, user_name, hide_tray_icon):
        pass

    def setLockoutType(self, user_name, lockout_type, wake_from, wake_to):
        pass

    def setTimeLeft(self, user_name, operation, time_left):
        pass

    def setPlayTimeEnabled(self, user_name, play_time_enabled):
        pass

    def setPlayTimeLimitOverride(self, user_name, play_time_limit_override):
        pass

    def setPlayTimeUnaccountedIntervalsEnabled(self, user_name, play_time_unaccounted_intervals_enabled):
        pass

    def setPlayTimeAllowedDays(self, user_name, play_time_allowed_days):
        pass

    def setPlayTimeLimitsForDays(self, user_name, play_time_limits):
        pass

    def setPlayTimeActivities(self, user_name, play_time_activities):
        pass

    def setPlayTimeLeft(self, user_name, operation, time_left):
        pass

    def getTimekprConfiguration(self):
        pass

    def setTimekprLogLevel(self, log_level):
        pass

    def setTimekprPollTime(self, poll_time_secs):
        pass

    def setTimekprSaveTime(self, save_time_secs):
        pass

    def setTimekprTrackInactive(self, track_inactive):
        pass

    def setTimekprTerminationTime(self, termination_time_secs):
        pass

    def setTimekprFinalWarningTime(self, final_warning_time_secs):
        pass

    def setTimekprFinalNotificationTime(self, final_notification_time_secs):
        pass

    def setTimekprSessionsCtrl(self, sessions_ctrl):
        pass

    def setTimekprSessionsExcl(self, sessions_excl):
        pass

    def setTimekprUsersExcl(self, users_excl):
        pass

    def setTimekprPlayTimeEnabled(self, play_time_enabled):
        pass

    def setTimekprPlayTimeEnhancedActivityMonitorEnabled(self, play_time_enabled):
        pass

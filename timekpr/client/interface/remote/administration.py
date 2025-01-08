"""
Created on Aug 28, 2018

@author: mjasnik
"""

from typing import Optional

from gi.repository import GLib

from timekpr.client.interface.remote.interface import timekprRemoteBus

# timekpr imports
from timekpr.common.constants import constants as cons
from timekpr.common.log import log
from timekpr.common.constants import messages as msg
from timekpr.common.utils.config import timekprConfig


class timekprRemoteAdminConnector(object):
    """Main class for remote connections through a relay remote server"""

    def __init__(self):
        """Initialize stuff for connecting to timekpr remote server"""
        # times
        self._retryTimeoutSecs = 3
        self._retryCountLeft = 5
        self._initFailed = False

        self._timekprObject: Optional[timekprRemoteBus] = None
        # configuration init
        self.timekpr_config = timekprConfig()
        # load config
        self.timekpr_config.loadMainConfiguration()

    def initTimekprConnection(self, try_once, reschedule_connection=False):
        """Init (connect to timekpr for info)"""
        # reschedule
        if reschedule_connection:
            # rescheduling means dropping existing state and try again
            self._timekprObject = None
            self._retryCountLeft = 5
            self._initFailed = False

        # only if notifications are ok
        if self._timekprObject is None:
            try:
                remote_host = self.timekpr_config._timekprConfig["TIMEKPR_REMOTE_HOST"]
                if remote_host is None:
                    log.consoleOut("NO remote host to connect to")
                remote_host = remote_host.rstrip("/")

                remote_access_token = self.timekpr_config._timekprConfig["TIMEKPR_REMOTE_ACCESS_TOKEN"]
                if remote_access_token is None:
                    log.consoleOut("NO remote access token")
                remote_host = remote_host.rstrip("/")
                # timekpr connection stuff
                self._timekprObject = timekprRemoteBus(remote_host, remote_access_token)
            except Exception:
                self._timekprObject = None
                # logging
                log.consoleOut("FAILED to obtain connection to timekpr remote server.\n")

        # if either of these fails, we keep trying to connect
        if self._timekprObject is None:
            if self._retryCountLeft > 0 and not try_once:
                log.consoleOut(
                    "connection failed, %i attempts left, will retry in %i seconds"
                    % (self._retryCountLeft, self._retryTimeoutSecs)
                )
                self._retryCountLeft -= 1

                # if either of this fails, we keep trying to connect
                GLib.timeout_add_seconds(3, self.initTimekprConnection, try_once)
            else:
                # failed
                self._initFailed = True

    # --------------- helper methods --------------- #

    def isConnected(self):
        """Return status of connection to DBUS"""
        # if either of these fails, we keep trying to connect
        return (
            self._timekprObject is not None,
            not self._initFailed,
        )

    def formatException(self, pExceptionStr, pFPath, pFName):
        """Format exception and pass it back"""
        # check for permission error
        if "org.freedesktop.DBus.Error.AccessDenied" in pExceptionStr:
            result = -1
            message = msg.getTranslation("TK_MSG_DBUS_COMMUNICATION_COMMAND_FAILED")
        else:
            result = -1
            message = msg.getTranslation("TK_MSG_UNEXPECTED_ERROR") % (
                '"%s" in "%s.%s"' % (pExceptionStr, pFPath, pFName)
            )
        # log error
        log.log(
            cons.TK_LOG_LEVEL_INFO,
            'ERROR: "%s" in "%s.%s"' % (pExceptionStr, pFPath, pFName),
        )
        # result
        return result, message

    def initReturnCodes(self, pInit, pCall):
        """Initialize the return codes for calls"""
        return -2 if pInit else -1 if pCall else 0, (
            msg.getTranslation("TK_MSG_STATUS_INTERFACE_NOTREADY")
            if pInit
            else (msg.getTranslation("TK_MSG_DBUS_COMMUNICATION_COMMAND_NOT_ACCEPTED") if pCall else "")
        )

    def getHostList(self):
        # defaults
        result, message = self.initReturnCodes(pInit=True, pCall=False)
        host_list = []

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message, host_list = self._timekprObject.getHostList()
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.getUserList.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message, host_list

    # --------------- user configuration info population methods --------------- #

    def getUserList(self):
        """Get user list from server"""
        # defaults
        result, message = self.initReturnCodes(pInit=True, pCall=False)
        userList = []

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message, userList = self._timekprObject.getUserList()
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.getUserList.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message, userList

    def getUserConfigurationAndInformation(self, pUserName, pInfoLvl):
        """Get user configuration from server"""
        # defaults
        result, message = self.initReturnCodes(pInit=True, pCall=False)
        userConfig = {}

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message, userConfig = self._timekprObject.getUserInformation(pUserName, pInfoLvl)
            except Exception as ex:
                # exception
                result, message = self.formatException(
                    str(ex), __name__, self.getUserConfigurationAndInformation.__name__
                )

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message, userConfig

    # --------------- user configuration set methods --------------- #

    def setAllowedDays(self, pUserName, pDayList):
        """Set user allowed days"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setAllowedDays(pUserName, pDayList)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setAllowedDays.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setAllowedHours(self, pUserName, pDayNumber, pHourList):
        """Set user allowed days"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setAllowedHours(pUserName, pDayNumber, pHourList)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setAllowedHours.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimeLimitForDays(self, pUserName, pDayLimits):
        """Set user allowed limit for days"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimeLimitForDays(pUserName, pDayLimits)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimeLimitForDays.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimeLimitForWeek(self, pUserName, pTimeLimitWeek):
        """Set user allowed limit for week"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimeLimitForWeek(pUserName, pTimeLimitWeek)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimeLimitForWeek.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimeLimitForMonth(self, user_name, time_limit_month):
        """Set user allowed limit for month"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimeLimitForMonth(user_name, time_limit_month)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimeLimitForMonth.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTrackInactive(self, user_name, track_inactive):
        """Set user allowed days"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTrackInactive(user_name, track_inactive)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.getUserList.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setHideTrayIcon(self, user_name, hide_tray_icon):
        """Set user allowed days"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setHideTrayIcon(user_name, hide_tray_icon)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setHideTrayIcon.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setLockoutType(self, user_name, lockout_type, wake_from, wake_to):
        """Set user restriction / lockout type"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setLockoutType(user_name, lockout_type, wake_from, wake_to)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setLockoutType.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimeLeft(self, user_name, operation, time_left):
        """Set user time left"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimeLeft(user_name, operation, time_left)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimeLeft.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    # --------------- PlayTime user configuration info set methods --------------- #

    def setPlayTimeEnabled(self, user_name, p_play_time_enabled):
        """Set PlayTime enabled flag for user"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setPlayTimeEnabled(user_name, p_play_time_enabled)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setPlayTimeEnabled.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setPlayTimeLimitOverride(self, user_name, p_play_time_limit_override):
        """Set PlayTime override flag for user"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setPlayTimeLimitOverride(user_name, p_play_time_limit_override)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setPlayTimeLimitOverride.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setPlayTimeUnaccountedIntervalsEnabled(self, user_name, play_time_unaccounted_intervals_enabled):
        """Set PlayTime allowed during unaccounted intervals flag for user"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setPlayTimeUnaccountedIntervalsEnabled(
                    user_name, play_time_unaccounted_intervals_enabled
                )
            except Exception as ex:
                # exception
                result, message = self.formatException(
                    str(ex),
                    __name__,
                    self.setPlayTimeUnaccountedIntervalsEnabled.__name__,
                )

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setPlayTimeAllowedDays(self, user_name, play_time_allowed_days):
        """Set allowed days for PlayTime for user"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setPlayTimeAllowedDays(user_name, play_time_allowed_days)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setPlayTimeAllowedDays.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setPlayTimeLimitsForDays(self, user_name, play_time_limits):
        """Set PlayTime limits for the allowed days for the user"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setPlayTimeLimitsForDays(user_name, play_time_limits)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setPlayTimeLimitsForDays.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setPlayTimeActivities(self, user_name, play_time_activities):
        """Set PlayTime limits for the allowed days for the user"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setPlayTimeActivities(user_name, play_time_activities)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setPlayTimeActivities.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setPlayTimeLeft(self, user_name, operation, time_left):
        """Set user time left"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setPlayTimeLeft(user_name, operation, time_left)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setPlayTimeLeft.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    # --------------- timekpr configuration info population / set methods --------------- #

    def getTimekprConfiguration(self):
        """Get configuration from server"""
        # defaults
        result, message = self.initReturnCodes(pInit=True, pCall=False)
        timekprConfig = {}

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message, timekprConfig = self._timekprObject.getTimekprConfiguration()
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.getTimekprConfiguration.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message, timekprConfig

    def setTimekprLogLevel(self, log_level):
        """Set the logging level for server"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprLogLevel(log_level)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprLogLevel.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprPollTime(self, poll_time_secs):
        """Set polltime for timekpr"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprPollTime(poll_time_secs)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprPollTime.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprSaveTime(self, save_time_secs):
        """Set save time for timekpr"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprSaveTime(save_time_secs)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprSaveTime.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprTrackInactive(self, track_inactive):
        """Set default value for tracking inactive sessions"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprTrackInactive(track_inactive)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprTrackInactive.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprTerminationTime(self, termination_time_secs):
        """Set up user termination time"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprTerminationTime(termination_time_secs)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprTerminationTime.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprFinalWarningTime(self, final_warning_time_secs):
        """Set up final warning time for users"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprFinalWarningTime(final_warning_time_secs)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprFinalWarningTime.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprFinalNotificationTime(self, final_notification_time_secs):
        """Set up final notification time for users"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprFinalNotificationTime(final_notification_time_secs)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprFinalNotificationTime.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprSessionsCtrl(self, sessions_ctrl):
        """Set accountable session types for users"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprSessionsCtrl(sessions_ctrl)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprSessionsCtrl.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprSessionsExcl(self, sessions_excl):
        """Set NON-accountable session types for users"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprSessionsExcl(sessions_excl)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprSessionsExcl.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprUsersExcl(self, users_excl):
        """Set excluded usernames for timekpr"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprUsersExcl(users_excl)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprUsersExcl.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprPlayTimeEnabled(self, play_time_enabled):
        """Set up global PlayTime enable switch"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprPlayTimeEnabled(play_time_enabled)
            except Exception as ex:
                # exception
                result, message = self.formatException(str(ex), __name__, self.setTimekprPlayTimeEnabled.__name__)

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

    def setTimekprPlayTimeEnhancedActivityMonitorEnabled(self, play_time_enabled):
        """Set up global PlayTime enhanced activity monitor enable switch"""
        # initial values
        result, message = self.initReturnCodes(pInit=True, pCall=False)

        # if we have end-point
        if self._timekprObject is not None:
            # defaults
            result, message = self.initReturnCodes(pInit=False, pCall=True)

            # notify through relay
            try:
                # call method
                result, message = self._timekprObject.setTimekprPlayTimeEnhancedActivityMonitorEnabled(
                    play_time_enabled
                )
            except Exception as ex:
                # exception
                result, message = self.formatException(
                    str(ex),
                    __name__,
                    self.setTimekprPlayTimeEnhancedActivityMonitorEnabled.__name__,
                )

                # we cannot send notif through relay, we need to reschedule connecton
                self.initTimekprConnection(False, True)

        # result
        return result, message

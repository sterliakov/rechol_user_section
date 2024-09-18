import { enqueueSnackbar } from 'notistack';
import type { ReactNode } from 'react';
import { useCallback } from 'react';
import { useIntl } from 'react-intl';

export type AlertSeverity = 'success' | 'warning' | 'error';

export default function useAlerts(): {
  showAlert: (
    severity: AlertSeverity,
    messageId: string,
    messageValues?: Record<string, ReactNode>,
  ) => void;
} {
  const { formatMessage } = useIntl();
  return {
    showAlert: useCallback(
      (
        severity: AlertSeverity,
        messageId: string,
        messageValues?: Record<string, ReactNode>,
      ) => {
        const messageText = formatMessage({ id: messageId }, messageValues);
        enqueueSnackbar({
          message: messageText,
          variant: severity,
        });
      },
      [formatMessage],
    ),
  };
}

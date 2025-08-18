import React from 'react';
import { Box, Typography } from '@mui/material';

const SettingsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom className="gradient-text">
        设置
      </Typography>
      <Typography variant="body1" color="text.secondary">
        这里将显示用户设置选项
      </Typography>
    </Box>
  );
};

export default SettingsPage;

import React from 'react';
import { Box, Typography } from '@mui/material';

const ReportsPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom className="gradient-text">
        分析报告
      </Typography>
      <Typography variant="body1" color="text.secondary">
        这里将显示所有的分析报告
      </Typography>
    </Box>
  );
};

export default ReportsPage;

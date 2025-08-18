import React from 'react';
import { Box, Typography } from '@mui/material';

const PricingPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom className="gradient-text">
        付费计划
      </Typography>
      <Typography variant="body1" color="text.secondary">
        这里将显示付费计划和价格
      </Typography>
    </Box>
  );
};

export default PricingPage;

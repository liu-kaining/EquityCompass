import React from 'react';
import { Box, Typography } from '@mui/material';

const StocksPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom className="gradient-text">
        股票池
      </Typography>
      <Typography variant="body1" color="text.secondary">
        这里将显示所有可选择的股票
      </Typography>
    </Box>
  );
};

export default StocksPage;

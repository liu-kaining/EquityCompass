import React from 'react';
import { Box, Typography } from '@mui/material';

const WatchlistPage: React.FC = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom className="gradient-text">
        关注列表
      </Typography>
      <Typography variant="body1" color="text.secondary">
        这里将显示您的个人关注列表
      </Typography>
    </Box>
  );
};

export default WatchlistPage;

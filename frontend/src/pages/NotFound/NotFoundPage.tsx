import React from 'react';
import { Box, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight="50vh"
      textAlign="center"
    >
      <Typography variant="h1" className="gradient-text" gutterBottom>
        404
      </Typography>
      <Typography variant="h5" gutterBottom>
        页面未找到
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom mb={3}>
        抱歉，您访问的页面不存在。
      </Typography>
      <Button
        variant="contained"
        color="primary"
        size="large"
        onClick={() => navigate('/dashboard')}
      >
        返回首页
      </Button>
    </Box>
  );
};

export default NotFoundPage;

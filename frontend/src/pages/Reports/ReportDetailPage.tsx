import React from 'react';
import { Box, Typography } from '@mui/material';
import { useParams } from 'react-router-dom';

const ReportDetailPage: React.FC = () => {
  const { reportId } = useParams<{ reportId: string }>();

  return (
    <Box>
      <Typography variant="h4" gutterBottom className="gradient-text">
        报告详情
      </Typography>
      <Typography variant="body1" color="text.secondary">
        报告ID: {reportId}
      </Typography>
    </Box>
  );
};

export default ReportDetailPage;

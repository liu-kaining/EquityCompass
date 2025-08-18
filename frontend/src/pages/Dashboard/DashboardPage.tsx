import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Chip,
} from '@mui/material';
import {
  TrendingUp,
  Assessment,
  Schedule,
  AccountBalanceWallet,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const statsCards = [
    {
      title: '关注股票',
      value: '0',
      icon: TrendingUp,
      color: 'primary.main',
      description: '当前关注的股票数量',
      action: () => navigate('/watchlist'),
    },
    {
      title: '分析报告',
      value: '0',
      icon: Assessment,
      color: 'success.main',
      description: '已生成的分析报告',
      action: () => navigate('/reports'),
    },
    {
      title: '待处理任务',
      value: '0',
      icon: Schedule,
      color: 'warning.main',
      description: '等待分析的任务',
      action: () => navigate('/analysis'),
    },
    {
      title: '剩余额度',
      value: user?.plan?.remaining_quota?.toString() || '0',
      icon: AccountBalanceWallet,
      color: 'info.main',
      description: '可用分析次数',
      action: () => navigate('/pricing'),
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom className="gradient-text">
        欢迎回来，{user?.nickname || user?.email}
      </Typography>
      
      <Typography variant="body1" color="text.secondary" gutterBottom mb={4}>
        这里是您的个人投资分析中心
      </Typography>

      {/* 用户计划状态 */}
      <Card sx={{ mb: 4 }} className="glass-effect">
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="center">
            <Box>
              <Typography variant="h6" gutterBottom>
                当前计划
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Chip
                  label={
                    user?.plan?.type === 'TRIAL'
                      ? '试用计划'
                      : user?.plan?.type === 'FREE'
                      ? '免费计划'
                      : user?.plan?.type === 'SUBSCRIPTION'
                      ? '订阅计划'
                      : '按次付费'
                  }
                  color="primary"
                  variant="filled"
                />
                <Typography variant="body2" color="text.secondary">
                  剩余 {user?.plan?.remaining_quota || 0} 次分析机会
                </Typography>
              </Box>
            </Box>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => navigate('/pricing')}
            >
              升级计划
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* 统计卡片 */}
      <Grid container spacing={3} mb={4}>
        {statsCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card 
              sx={{ 
                cursor: 'pointer',
                transition: 'transform 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                }
              }}
              className="glass-effect"
              onClick={card.action}
            >
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 2,
                      bgcolor: card.color,
                      color: 'white',
                      mr: 2,
                    }}
                  >
                    <card.icon />
                  </Box>
                  <Typography variant="h4" component="div">
                    {card.value}
                  </Typography>
                </Box>
                <Typography variant="h6" gutterBottom>
                  {card.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {card.description}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* 快速操作 */}
      <Card className="glass-effect">
        <CardContent>
          <Typography variant="h6" gutterBottom>
            快速操作
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="contained"
                color="primary"
                onClick={() => navigate('/stocks')}
                sx={{ py: 2 }}
              >
                浏览股票池
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                color="primary"
                onClick={() => navigate('/watchlist')}
                sx={{ py: 2 }}
              >
                管理关注列表
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                color="secondary"
                onClick={() => navigate('/analysis')}
                sx={{ py: 2 }}
              >
                开始分析
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button
                fullWidth
                variant="outlined"
                color="info"
                onClick={() => navigate('/reports')}
                sx={{ py: 2 }}
              >
                查看报告
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default DashboardPage;

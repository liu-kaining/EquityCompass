import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Container,
  Step,
  Stepper,
  StepLabel,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sendVerificationCode, login } = useAuth();
  
  const [activeStep, setActiveStep] = useState(0);
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const steps = ['输入邮箱', '验证登录'];

  const handleSendCode = async () => {
    if (!email) {
      setError('请输入邮箱地址');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      await sendVerificationCode(email);
      setSuccess('验证码已发送，请查收邮件');
      setActiveStep(1);
    } catch (err: any) {
      setError(err.message || '发送验证码失败');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyCode = async () => {
    if (!code) {
      setError('请输入验证码');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      await login(email, code);
      const from = (location.state as any)?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    } catch (err: any) {
      setError(err.message || '验证失败');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setActiveStep(0);
    setCode('');
    setError(null);
    setSuccess(null);
  };

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        justifyContent="center"
        alignItems="center"
        minHeight="100vh"
        py={4}
      >
        <Typography
          variant="h3"
          component="h1"
          gutterBottom
          className="gradient-text"
          textAlign="center"
        >
          智策股析
        </Typography>
        
        <Typography
          variant="h6"
          color="text.secondary"
          gutterBottom
          textAlign="center"
          mb={4}
        >
          每日股价分析与决策平台
        </Typography>

        <Card sx={{ width: '100%', maxWidth: 400 }} className="glass-effect">
          <CardContent sx={{ p: 4 }}>
            <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
              {steps.map((label) => (
                <Step key={label}>
                  <StepLabel>{label}</StepLabel>
                </Step>
              ))}
            </Stepper>

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {success && (
              <Alert severity="success" sx={{ mb: 2 }}>
                {success}
              </Alert>
            )}

            {activeStep === 0 && (
              <Box>
                <TextField
                  fullWidth
                  label="邮箱地址"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  variant="outlined"
                  sx={{ mb: 3 }}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendCode()}
                />
                
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleSendCode}
                  disabled={loading}
                  sx={{ mb: 2 }}
                >
                  {loading ? '发送中...' : '发送验证码'}
                </Button>
                
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  输入邮箱即可登录或注册
                </Typography>
              </Box>
            )}

            {activeStep === 1 && (
              <Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  验证码已发送至：{email}
                </Typography>
                
                <TextField
                  fullWidth
                  label="6位验证码"
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  variant="outlined"
                  sx={{ mb: 3 }}
                  inputProps={{ maxLength: 6 }}
                  onKeyPress={(e) => e.key === 'Enter' && handleVerifyCode()}
                />
                
                <Button
                  fullWidth
                  variant="contained"
                  size="large"
                  onClick={handleVerifyCode}
                  disabled={loading}
                  sx={{ mb: 2 }}
                >
                  {loading ? '验证中...' : '验证登录'}
                </Button>
                
                <Button
                  fullWidth
                  variant="text"
                  onClick={handleBack}
                  disabled={loading}
                >
                  返回上一步
                </Button>
              </Box>
            )}
          </CardContent>
        </Card>

        <Typography variant="body2" color="text.secondary" textAlign="center" mt={3}>
          登录即表示您同意我们的服务条款和隐私政策
        </Typography>
      </Box>
    </Container>
  );
};

export default LoginPage;

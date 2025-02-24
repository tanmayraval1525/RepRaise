// pages/index.tsx
import { useState } from 'react';
import { Button, Input, Stack, Text, Heading,Box,ClientOnly,Skeleton } from '@chakra-ui/react';
import { useRouter } from 'next/router';
import axios from 'axios';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { ColorModeToggle } from "../components/ui/color-mode-toggle"
import api from '../utils/api';

type AuthFormData = {
  email: string;
  password: string;
  firstName?: string;
  lastName?: string;
  confirmPassword?: string;
};

const LoginPage = () => {
  const loginSchema = yup.object().shape({
    email: yup.string().email('Invalid email').required('Email is required'),
    password: yup.string().min(8, 'Password must be at least 8 characters').required('Password is required'),
  });
  
  const signupSchema = yup.object().shape({
    firstName: yup.string().required('First name is required'),
    lastName: yup.string(),
    email: yup.string().email('Invalid email').required('Email is required'),
    password: yup
    .string()
    .required("Password is required")
    .min(8, "Password must be at least 8 characters")
    .matches(/[A-Z]/, "Password must contain at least 1 uppercase letter")
    .matches(/[a-z]/, "Password must contain at least 1 lowercase letter")
    .matches(/\d/, "Password must contain at least 1 number")
    .matches(/[@$!%*?&]/, "Password must contain at least 1 special character"),
    confirmPassword: yup
      .string()
      .oneOf([yup.ref('password')], 'Passwords must match')
      .required('Confirm Password is required'),
  });
  const [isLogin, setIsLogin] = useState(true);
  const [errorMessage, setErrorMessage] = useState("");
  const router = useRouter();

  

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<AuthFormData>({
    resolver: yupResolver(isLogin ? loginSchema : signupSchema),
  });

  const onSubmit = async (data: AuthFormData) => {
    const url = isLogin ? '/login' : '/signup';
    //const data = isLogin ? { email, password } : { email, password, fname, lname };

    try {
      console.log(data);
      const response = await api.post(url, data);
      
      if (response.status === 200) {
        // Handle success - you can store tokens or redirect to another page
        router.push(isLogin ? '/dashboard' : '/login');
      }
    } catch (error) {
      // Handle error
      if (axios.isAxiosError(error) && error.response) {
        // Extract the error message sent by the backend
        setErrorMessage(error.response.data.error || "An error occurred");
      } else {
        setErrorMessage("An unknown error occurred");
      }
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '0 auto', paddingTop: '50px' }}>
      <Box pos="absolute" top="4" right="4">
        <ClientOnly fallback={<Skeleton w="10" h="10" rounded="md" />}>
          <ColorModeToggle />
        </ClientOnly>
      </Box>
      <Heading textAlign="center">{isLogin ? 'Login' : 'Sign Up'}</Heading>
      <form onSubmit={handleSubmit(onSubmit)}>
        <Stack>
        <Box>
            <Input type="email" placeholder="Email" {...register('email')} />
            {errors.email && <Text color="red.500">{errors.email.message}</Text>}
        </Box>

        <Box>
                <Input type="password" placeholder="Password" {...register('password')} />
                {errors.password && <Text color="red.500">{errors.password.message}</Text>}
        </Box>
        
        {!isLogin && (
            <>
              <Box>
                <Input type="text" placeholder="First Name" {...register('firstName')} />
                {errors.firstName && <Text color="red.500">{errors.firstName.message}</Text>}
              </Box>

              <Box>
                <Input type="text" placeholder="Last Name" {...register('lastName')} />
                {errors.lastName && <Text color="red.500">{errors.lastName.message}</Text>}
              </Box>

              <Box>
                <Input type="password" placeholder="Confirm Password" {...register('confirmPassword')} />
                {errors.confirmPassword && <Text color="red.500">{errors.confirmPassword.message}</Text>}
              </Box>
            </>
          )}
          
          

          

          <Button type="submit" colorScheme="teal" width="full">
            {isLogin ? 'Login' : 'Sign Up'}
          </Button>

          {errorMessage && <div style={{ color: "red" }}>{errorMessage}</div>}
        </Stack>
      </form>
      <Text textAlign="center" mt="4">
        {isLogin ? "Don't have an account?" : 'Already have an account?'}{' '}
        <Button variant="ghost" onClick={() => setIsLogin(!isLogin)}>
          {isLogin ? 'Sign Up' : 'Login'}
        </Button>
      </Text>
    </div>
  );
};

export default LoginPage;

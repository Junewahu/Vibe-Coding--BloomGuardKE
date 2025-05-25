import React, { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Stack,
  Textarea,
  useToast,
  Grid,
  GridItem,
  FormErrorMessage,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from '@chakra-ui/react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { usePatientStore } from '../../stores/patientStore';

// Validation schema
const patientSchema = z.object({
  first_name: z.string().min(2, 'First name is required'),
  last_name: z.string().min(2, 'Last name is required'),
  date_of_birth: z.string().refine((date) => new Date(date) < new Date(), {
    message: 'Date of birth must be in the past',
  }),
  gender: z.enum(['male', 'female', 'other']),
  phone_number: z.string().min(10, 'Valid phone number required'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  address: z.string().min(5, 'Address is required'),
  county: z.string().min(2, 'County is required'),
  sub_county: z.string().min(2, 'Sub-county is required'),
  nhif_number: z.string().optional(),
  blood_type: z.string().optional(),
  allergies: z.array(z.string()).optional(),
  chronic_conditions: z.array(z.string()).optional(),
  medical_history: z.record(z.any()).optional(),
});

type PatientFormData = z.infer<typeof patientSchema>;

export const PatientRegistrationForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();
  const { createPatient } = usePatientStore();

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<PatientFormData>({
    resolver: zodResolver(patientSchema),
  });

  const onSubmit = async (data: PatientFormData) => {
    try {
      setIsLoading(true);
      await createPatient(data);
      toast({
        title: 'Patient registered successfully',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
      navigate('/patients');
    } catch (error) {
      toast({
        title: 'Error registering patient',
        description: error instanceof Error ? error.message : 'An error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box as="form" onSubmit={handleSubmit(onSubmit)} p={4}>
      <Stack spacing={4}>
        <Grid templateColumns="repeat(2, 1fr)" gap={4}>
          <GridItem>
            <FormControl isInvalid={!!errors.first_name}>
              <FormLabel>First Name</FormLabel>
              <Input {...register('first_name')} />
              <FormErrorMessage>{errors.first_name?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.last_name}>
              <FormLabel>Last Name</FormLabel>
              <Input {...register('last_name')} />
              <FormErrorMessage>{errors.last_name?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.date_of_birth}>
              <FormLabel>Date of Birth</FormLabel>
              <Input type="date" {...register('date_of_birth')} />
              <FormErrorMessage>{errors.date_of_birth?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.gender}>
              <FormLabel>Gender</FormLabel>
              <Select {...register('gender')}>
                <option value="">Select gender</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </Select>
              <FormErrorMessage>{errors.gender?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.phone_number}>
              <FormLabel>Phone Number</FormLabel>
              <Input {...register('phone_number')} />
              <FormErrorMessage>{errors.phone_number?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.email}>
              <FormLabel>Email (Optional)</FormLabel>
              <Input type="email" {...register('email')} />
              <FormErrorMessage>{errors.email?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem colSpan={2}>
            <FormControl isInvalid={!!errors.address}>
              <FormLabel>Address</FormLabel>
              <Textarea {...register('address')} />
              <FormErrorMessage>{errors.address?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.county}>
              <FormLabel>County</FormLabel>
              <Input {...register('county')} />
              <FormErrorMessage>{errors.county?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.sub_county}>
              <FormLabel>Sub-county</FormLabel>
              <Input {...register('sub_county')} />
              <FormErrorMessage>{errors.sub_county?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.nhif_number}>
              <FormLabel>NHIF Number (Optional)</FormLabel>
              <Input {...register('nhif_number')} />
              <FormErrorMessage>{errors.nhif_number?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>

          <GridItem>
            <FormControl isInvalid={!!errors.blood_type}>
              <FormLabel>Blood Type (Optional)</FormLabel>
              <Select {...register('blood_type')}>
                <option value="">Select blood type</option>
                <option value="A+">A+</option>
                <option value="A-">A-</option>
                <option value="B+">B+</option>
                <option value="B-">B-</option>
                <option value="AB+">AB+</option>
                <option value="AB-">AB-</option>
                <option value="O+">O+</option>
                <option value="O-">O-</option>
              </Select>
              <FormErrorMessage>{errors.blood_type?.message}</FormErrorMessage>
            </FormControl>
          </GridItem>
        </Grid>

        <Button
          type="submit"
          colorScheme="blue"
          isLoading={isLoading}
          loadingText="Registering..."
        >
          Register Patient
        </Button>
      </Stack>
    </Box>
  );
}; 
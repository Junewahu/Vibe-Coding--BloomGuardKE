import React, { useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Stack,
  Grid,
  FormErrorMessage,
  useToast,
  Textarea,
  Checkbox,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
} from '@chakra-ui/react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useParams, useNavigate } from 'react-router-dom';
import { usePatient } from '../../hooks/usePatient';
import { Patient } from '../../types/patient';

const patientSchema = z.object({
  first_name: z.string().min(1, 'First name is required'),
  last_name: z.string().min(1, 'Last name is required'),
  date_of_birth: z.string().min(1, 'Date of birth is required'),
  gender: z.enum(['male', 'female', 'other']),
  contact_info: z.object({
    phone: z.string().min(1, 'Phone number is required'),
    email: z.string().email('Invalid email').optional(),
    address: z.object({
      street: z.string().min(1, 'Street is required'),
      city: z.string().min(1, 'City is required'),
      county: z.string().min(1, 'County is required'),
      postal_code: z.string().optional(),
      coordinates: z.object({
        latitude: z.number(),
        longitude: z.number(),
      }).optional(),
    }),
    alternative_phone: z.string().optional(),
  }),
  demographics: z.object({
    ethnicity: z.string().optional(),
    language_preference: z.string().min(1, 'Language preference is required'),
    education_level: z.string().optional(),
    occupation: z.string().optional(),
    insurance_provider: z.string().optional(),
    insurance_number: z.string().optional(),
  }),
  medical_history: z.object({
    allergies: z.array(z.string()),
    chronic_conditions: z.array(z.string()),
    previous_surgeries: z.array(z.string()),
    family_history: z.array(z.string()),
    current_medications: z.array(z.string()),
  }),
  biometrics: z.object({
    fingerprint_id: z.string().optional(),
    facial_id: z.string().optional(),
    photo_url: z.string().optional(),
  }).optional(),
  status: z.enum(['active', 'inactive', 'deceased']),
  flags: z.object({
    incomplete_record: z.boolean(),
    high_risk: z.boolean(),
    special_needs: z.boolean(),
    requires_follow_up: z.boolean(),
  }),
});

type PatientFormData = z.infer<typeof patientSchema>;

export const PatientEditForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const toast = useToast();

  const {
    selectedPatient: patient,
    isLoading,
    getPatient,
    updatePatient,
  } = usePatient();

  const {
    register,
    handleSubmit,
    control,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<PatientFormData>({
    resolver: zodResolver(patientSchema),
  });

  useEffect(() => {
    if (id) {
      getPatient(id);
    }
  }, [id, getPatient]);

  useEffect(() => {
    if (patient) {
      reset({
        ...patient,
        date_of_birth: new Date(patient.date_of_birth).toISOString().split('T')[0],
      });
    }
  }, [patient, reset]);

  const onSubmit = async (data: PatientFormData) => {
    try {
      await updatePatient(id!, data);
      toast({
        title: 'Patient updated successfully',
        status: 'success',
        duration: 3000,
      });
      navigate(`/patients/${id}`);
    } catch (error) {
      // Error is handled by the hook
    }
  };

  if (isLoading) {
    return null;
  }

  return (
    <Box as="form" onSubmit={handleSubmit(onSubmit)}>
      <Stack spacing={6}>
        {/* Basic Information */}
        <Box>
          <Grid templateColumns="repeat(2, 1fr)" gap={6}>
            <FormControl isInvalid={!!errors.first_name}>
              <FormLabel>First Name</FormLabel>
              <Input {...register('first_name')} />
              <FormErrorMessage>{errors.first_name?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.last_name}>
              <FormLabel>Last Name</FormLabel>
              <Input {...register('last_name')} />
              <FormErrorMessage>{errors.last_name?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.date_of_birth}>
              <FormLabel>Date of Birth</FormLabel>
              <Input type="date" {...register('date_of_birth')} />
              <FormErrorMessage>{errors.date_of_birth?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.gender}>
              <FormLabel>Gender</FormLabel>
              <Select {...register('gender')}>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other</option>
              </Select>
              <FormErrorMessage>{errors.gender?.message}</FormErrorMessage>
            </FormControl>
          </Grid>
        </Box>

        {/* Contact Information */}
        <Box>
          <Grid templateColumns="repeat(2, 1fr)" gap={6}>
            <FormControl isInvalid={!!errors.contact_info?.phone}>
              <FormLabel>Phone</FormLabel>
              <Input {...register('contact_info.phone')} />
              <FormErrorMessage>{errors.contact_info?.phone?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.contact_info?.email}>
              <FormLabel>Email</FormLabel>
              <Input {...register('contact_info.email')} />
              <FormErrorMessage>{errors.contact_info?.email?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.contact_info?.address?.street}>
              <FormLabel>Street</FormLabel>
              <Input {...register('contact_info.address.street')} />
              <FormErrorMessage>{errors.contact_info?.address?.street?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.contact_info?.address?.city}>
              <FormLabel>City</FormLabel>
              <Input {...register('contact_info.address.city')} />
              <FormErrorMessage>{errors.contact_info?.address?.city?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.contact_info?.address?.county}>
              <FormLabel>County</FormLabel>
              <Input {...register('contact_info.address.county')} />
              <FormErrorMessage>{errors.contact_info?.address?.county?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.contact_info?.address?.postal_code}>
              <FormLabel>Postal Code</FormLabel>
              <Input {...register('contact_info.address.postal_code')} />
              <FormErrorMessage>{errors.contact_info?.address?.postal_code?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.contact_info?.alternative_phone}>
              <FormLabel>Alternative Phone</FormLabel>
              <Input {...register('contact_info.alternative_phone')} />
              <FormErrorMessage>{errors.contact_info?.alternative_phone?.message}</FormErrorMessage>
            </FormControl>
          </Grid>
        </Box>

        {/* Demographics */}
        <Box>
          <Grid templateColumns="repeat(2, 1fr)" gap={6}>
            <FormControl isInvalid={!!errors.demographics?.ethnicity}>
              <FormLabel>Ethnicity</FormLabel>
              <Input {...register('demographics.ethnicity')} />
              <FormErrorMessage>{errors.demographics?.ethnicity?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.demographics?.language_preference}>
              <FormLabel>Language Preference</FormLabel>
              <Input {...register('demographics.language_preference')} />
              <FormErrorMessage>{errors.demographics?.language_preference?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.demographics?.education_level}>
              <FormLabel>Education Level</FormLabel>
              <Input {...register('demographics.education_level')} />
              <FormErrorMessage>{errors.demographics?.education_level?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.demographics?.occupation}>
              <FormLabel>Occupation</FormLabel>
              <Input {...register('demographics.occupation')} />
              <FormErrorMessage>{errors.demographics?.occupation?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.demographics?.insurance_provider}>
              <FormLabel>Insurance Provider</FormLabel>
              <Input {...register('demographics.insurance_provider')} />
              <FormErrorMessage>{errors.demographics?.insurance_provider?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.demographics?.insurance_number}>
              <FormLabel>Insurance Number</FormLabel>
              <Input {...register('demographics.insurance_number')} />
              <FormErrorMessage>{errors.demographics?.insurance_number?.message}</FormErrorMessage>
            </FormControl>
          </Grid>
        </Box>

        {/* Medical History */}
        <Box>
          <Grid templateColumns="repeat(2, 1fr)" gap={6}>
            <FormControl isInvalid={!!errors.medical_history?.allergies}>
              <FormLabel>Allergies</FormLabel>
              <Textarea
                {...register('medical_history.allergies')}
                placeholder="Enter allergies, one per line"
              />
              <FormErrorMessage>{errors.medical_history?.allergies?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.medical_history?.chronic_conditions}>
              <FormLabel>Chronic Conditions</FormLabel>
              <Textarea
                {...register('medical_history.chronic_conditions')}
                placeholder="Enter chronic conditions, one per line"
              />
              <FormErrorMessage>{errors.medical_history?.chronic_conditions?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.medical_history?.previous_surgeries}>
              <FormLabel>Previous Surgeries</FormLabel>
              <Textarea
                {...register('medical_history.previous_surgeries')}
                placeholder="Enter previous surgeries, one per line"
              />
              <FormErrorMessage>{errors.medical_history?.previous_surgeries?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.medical_history?.family_history}>
              <FormLabel>Family History</FormLabel>
              <Textarea
                {...register('medical_history.family_history')}
                placeholder="Enter family history, one per line"
              />
              <FormErrorMessage>{errors.medical_history?.family_history?.message}</FormErrorMessage>
            </FormControl>

            <FormControl isInvalid={!!errors.medical_history?.current_medications}>
              <FormLabel>Current Medications</FormLabel>
              <Textarea
                {...register('medical_history.current_medications')}
                placeholder="Enter current medications, one per line"
              />
              <FormErrorMessage>{errors.medical_history?.current_medications?.message}</FormErrorMessage>
            </FormControl>
          </Grid>
        </Box>

        {/* Flags */}
        <Box>
          <Grid templateColumns="repeat(4, 1fr)" gap={6}>
            <FormControl>
              <Checkbox {...register('flags.incomplete_record')}>Incomplete Record</Checkbox>
            </FormControl>

            <FormControl>
              <Checkbox {...register('flags.high_risk')}>High Risk</Checkbox>
            </FormControl>

            <FormControl>
              <Checkbox {...register('flags.special_needs')}>Special Needs</Checkbox>
            </FormControl>

            <FormControl>
              <Checkbox {...register('flags.requires_follow_up')}>Requires Follow-up</Checkbox>
            </FormControl>
          </Grid>
        </Box>

        {/* Status */}
        <FormControl isInvalid={!!errors.status}>
          <FormLabel>Status</FormLabel>
          <Select {...register('status')}>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="deceased">Deceased</option>
          </Select>
          <FormErrorMessage>{errors.status?.message}</FormErrorMessage>
        </FormControl>

        {/* Submit Buttons */}
        <Stack direction="row" spacing={4} justify="flex-end">
          <Button onClick={() => navigate(`/patients/${id}`)}>Cancel</Button>
          <Button
            type="submit"
            colorScheme="blue"
            isLoading={isSubmitting}
          >
            Save Changes
          </Button>
        </Stack>
      </Stack>
    </Box>
  );
}; 
KPL/MK
\begintext


   File name                   Contents
   --------------------------  -----------------------------
   naif0008.tls                Generic LSK
   cas00084.tsc                Cassini SCLK
   981005_PLTEPH-DE405S.bsp    Solar System Ephemeris
   020514_SE_SAT105.bsp        Saturnian Satellite Ephemeris
   030201AP_SK_SM546_T45.bsp   Cassini Spacecraft SPK
   cas_v37.tf                  Cassini FK
   04135_04171pc_psiv2.bc      Cassini Spacecraft CK
   cpck05Mar2004.tpc           Cassini Project PCK
   cas_iss_v09.ti              ISS Instrument Kernel
   phoebe_64q.bds              Phoebe DSK


   \begindata
   KERNELS_TO_LOAD = ( '../../SALSA/test_kernels/naif0008.tls',
                       '../../SALSA/test_kernels/cas00084.tsc',
                       '../../SALSA/test_kernels/981005_PLTEPH-DE405S.bsp',
                       '../../SALSA/test_kernels/020514_SE_SAT105.bsp',
                       '../../SALSA/test_kernels/030201AP_SK_SM546_T45.bsp',
                       '../../SALSA/test_kernels/cas_v37.tf',
                       '../../SALSA/test_kernels/04135_04171pc_psiv2.bc',
                       '../../SALSA/test_kernels/cpck05Mar2004.tpc',
                       '../../SALSA/test_kernels/cas_iss_v09.ti'
                       '../../SALSA/test_kernels/phoebe_64q.bds' )
   \begintext
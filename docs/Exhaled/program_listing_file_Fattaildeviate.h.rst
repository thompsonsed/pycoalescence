
.. _program_listing_file_Fattaildeviate.h:

Program Listing for File Fattaildeviate.h
========================================================================================

- Return to documentation for :ref:`file_Fattaildeviate.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under BSD-3 license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/BSD-3-Clause) for full license details.
   
   #ifndef FATTAIL_H
   #define FATTAIL_H
   #define IM1 2147483563
   #define IM2 2147483399
   #define AM (1.0/IM1)
   #define IMM1 (IM1-1)
   #define IA1 40014
   #define IA2 40692
   #define IQ1 53668
   #define IQ2 5277
   #define IR1 12211
   #define IR2 3791
   #define NTAB 32
   #define NDIV (1+IMM1/NTAB)
   #define EPS 1.2e-8
   #define RNMX (1.0-EPS)
   
   # include <stdio.h>
   # include <string>
   # include <iomanip>
   # include <math.h>
   # include <vector>
   # include <iostream>
   # include <fstream>
   #include "Logging.h"
   
   using namespace std;
   
   class NRrand {
   
   private:
       long idum;
       int j;
       long k;
       long idum2;
       long iy;
       long iv[NTAB];
       double temp;
       bool seeded;
   
       double lastresult;
       bool normflag;
       // for the L value of the dispersal kernel (the width - does not affect the shape).
       double tau;
       // for the sigma value of the dispersal kernel (the variance of a normal distribution).
       double sigma;
       typedef double (NRrand::*fptr)(); // once setup will contain the dispersal function to use for this simulation.
       fptr dispersalFunction;
       // the probability that dispersal comes from the uniform distribution. This is only relevant for uniform dispersals.
       double m_prob;
       // the cutoff for the uniform dispersal function i.e. the maximum value to be drawn from the uniform distribution.
       double cutoff;
   public:
   
       NRrand()
       {
           seeded = false;
           normflag = true;
           dispersalFunction = nullptr;
           sigma = 0;
           tau = 0;
       }
   
       void setSeed(long seed)
       {
           if (!seeded)
           {
           idum2 = 123456789;
           iy = 0;
           idum = seed;
           if (idum < 1) idum=1; 
           //Be sure to prevent idum = 0.
           idum2=(idum);
           for (j=NTAB+7;j>=0;j--) 
           {
               //Load the shuffle table (after 8 warm-ups).
               k=(idum)/IQ1;
               idum=IA1*(idum-k*IQ1)-k*IR1;
               if (idum < 0) idum += IM1;
               if (j < NTAB) iv[j] = idum;
             }
           iy=iv[0];
           seeded = true;
           }
           else
           {
               throw runtime_error("Trying to set the seed again: this can only be set once.");
           }
       }
   
       double d01()
       {
           k=(idum)/IQ1; 
           //Start here when not initializing.
           idum=IA1*(idum-k*IQ1)-k*IR1; 
           //Compute idum=(IA1*idum) % IM1 without overflows by Schrage's method. 
           if (idum < 0) idum += IM1;
           k=idum2/IQ2;
           idum2=IA2*(idum2-k*IQ2)-k*IR2; 
           //Compute idum2=(IA2*idum) % IM2 likewise.
           if (idum2 < 0) idum2 += IM2;
           j=iy/NDIV; 
           //Will be in the range 0..NTAB-1.
           iy=iv[j]-idum2; 
           //Here idum is shuffled, idum and idum2 are combined to generate output. 
           iv[j] = idum;
           if (iy < 1) iy += IMM1;
           if ((temp=AM*iy) > RNMX) 
           {
               //os << "random call = " << "RNMAX" << "\n";
               return RNMX; //Because users don't expect endpoint values.
           }
           else 
           {
               
               return temp;
           }
       }  
   
       long i0(long max)
       {
           //long temp = (long(d01()*(max+1)));
           //os << "random call = " << temp << "\n";
           return (long(d01()*(max+1)));
       }
       
       double norm()
       {
           if (normflag)
           {
               double r2 = 2;
               double xx;
               double yy;
               while (r2>1)
               {
                   xx=2.0*d01()-1.0;
                   yy=2.0*d01()-1.0;
                   r2=(xx*xx)+(yy*yy);
               }
               double fac=sqrt(-2.0*log(r2)/r2);
               lastresult = xx*fac;
               double result = yy*fac;
               normflag = false;
               return sigma * result;
           }
           else
           {
               normflag = true;
               return sigma * lastresult;
           }
       }
       
       double norm2D()
       {
           double distx, disty;
           distx = norm();
           disty = norm();
           return pow(pow(distx,2)+ pow(disty,2),0.5);
       }
   
       void setDispersalParams(const double sigmain, const double tauin)
       {
           sigma = sigmain;
           tau = tauin; // used to invert the sign here, doesn't any more.
       }
       
   
       double fattail(double z)
       {
           double result;
           result = pow((pow(d01(),(1.0/(1.0-z)))-1.0), 0.5);
           return result;
       }
   
       // this new version corrects the 1.0 to 2.0 and doesn't require the values to be passed every time.
       double fattail()
       {
           double result;
           // old function version (kept for reference)
   //      result = (tau * pow((pow(d01(),(2.0/(2.0-sigma)))-1.0),0.5));
           result = (sigma * pow((tau * (pow(d01(), double(-2.0 / tau)))-1.0), 0.5));
           return result;
       }
       
       double fattail_old()
       {
           double result;
           result = (sigma * pow((pow(d01(), (2.0/(2.0+tau)))-1.0), 0.5));
           return result;
       }
   
       double direction()
       {
           double xx = 1.0 , yy = 1.0;
           while (xx*xx+yy*yy>1.0)
           {
           xx = d01();
           yy = d01();
           }
           return pow((xx/yy),2.0);
       }
   
       bool event(double probin)
       {
           if (probin < 0.000001)
           {
               if (d01() <= 0.000001)
               {
                   return (event(probin * 1000000.0));
               }
               else
               {
                   return false;
               }
           }
           else
           {
               if (probin > 0.999999)
               {
                   return (!(event(1.0-probin)));
               }
               else
               {
                   return (d01() <= probin);
               }
           }
       }
       
       double normUniform()
       {
           // Check if the dispersal event comes from the uniform distribution
           if(d01() < m_prob)
           {
               // Then it does come from the uniform distribution
               return (d01() * cutoff);
           }
           else
           {
               return norm2D();
           }
       }
       
       
       void setDispersalMethod(const string &dispersal_method, const double & m_probin, const double & cutoffin)
       {
           if (dispersal_method == "normal")
           {
               dispersalFunction = &NRrand::norm2D;
               if(sigma < 0)
               {
                   throw invalid_argument("Cannot have negative sigma with normal dispersal");
               }
           }
           else if (dispersal_method == "fat-tail")
           {
               dispersalFunction = &NRrand::fattail;
               if(tau < 0 || sigma  < 0)
               {
                   throw invalid_argument("Cannot have negative sigma or tau with fat-tailed dispersal");
               }
           }
           else if (dispersal_method == "norm-uniform")
           {
               dispersalFunction = &NRrand::normUniform;
               if(sigma  < 0)
               {
                   throw invalid_argument("Cannot have negative sigma with normal dispersal");
               }
           }
           // Also provided the old version of the fat-tailed dispersal kernel
           else if(dispersal_method == "fat-tail-old")
           {
               dispersalFunction = &NRrand::fattail_old;
               if(tau > -2 || sigma  < 0)
               {
                   throw invalid_argument("Cannot have sigma < 0 or tau > -2 with fat-tailed dispersal (old implementation).");
               }
           }
           else
           {
               throw runtime_error("Dispersal method not detected. Check implementation exists");
           }
           m_prob = m_probin;
           cutoff = cutoffin;
       }
       
       
       double dispersal()
       {
           return (this->*dispersalFunction)();
       }
       
       // to reconstruct distribution, use x = fattail/squrt(1+direction) , y = fattail/squrt(1+(direction^-1))
   
       friend ostream& operator<<(ostream& os,const NRrand& r) 
       {
           //os << m.numRows<<" , "<<m.numCols<<" , "<<endl; 
           os << setprecision(64);
           os << r.idum << ",";
           os << r.j << ",";
           os << r.k << ",";
           os << r.idum2 << ",";
           os << r.iy << ",";
           for(int i=0;i<NTAB;i++)
           {
               os << r.iv[i] << ",";
           }
           os << r.temp << ",";
           os << r.seeded << ",";
           os << r.lastresult << ",";
           os << r.normflag << "," << r.tau << "," << r.sigma << "," << r.m_prob << "," << r.cutoff;
           return os;
       }
   
       friend istream& operator>>(istream& is, NRrand& r) 
       {
   //      os << "starting NR read" << endl;
           char delim;
           //double temp1,temp2;
           //is << m.numRows<<" , "<<m.numCols<<" , "<<endl; 
           is >> r.idum;
   //      os << r.idum << endl;
   //      string tmp;
   //      is >> delim >> tmp;
   //      os << tmp << endl;
   //      os << delim;
           is >> delim;
           is >> r.j;
           is >> delim;
           is >> r.k;
           is >> delim;
           is >> r.idum2;
           is >> delim;
           is >> r.iy;
           is >> delim;
           for(int i=0;i<NTAB;i++)
           {
               is >> r.iv[i];
               is >> delim;
           }
           is >> r.temp;
           is >> delim;
           is >> r.seeded;
           is >> delim;
           is >> r.lastresult;
           is >> delim;
           is >>r.normflag;
           is >> delim >> r.tau >> delim >> r.sigma >> delim >> r.m_prob >> delim >> r.cutoff;
           return is;
       }
   };
   #endif

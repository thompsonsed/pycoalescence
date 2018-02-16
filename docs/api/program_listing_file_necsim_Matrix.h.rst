
.. _program_listing_file_necsim_Matrix.h:

Program Listing for File Matrix.h
=================================

- Return to documentation for :ref:`file_necsim_Matrix.h`

.. code-block:: cpp

   
   #ifndef MATRIX
   # define MATRIX
   # define null 0
   # include <cstdio>
   #include <iostream>
   #include <sstream>
   #include <fstream>
   #include <cstdlib>
   #include <cstring>
   #include <stdexcept>
   
   #ifdef use_csv
   #include<cmath>
   #include <stdexcept>
   #include "fast-cpp-csv-parser/csv.h"
   #endif
   #ifdef with_gdal
   
   #include <gdal_priv.h>
   #include <cpl_conv.h> // for CPLMalloc()
   
   #endif
   
   #include <cstdint>
   #include "Logging.h"
   
   using namespace std;
   
   // Array of data sizes for importing tif files.
   const int gdal_data_sizes[] = {0, 8, 16, 16, 32, 32, 32, 64};
   
   template<class T>
   class Row
   {
   private:
       // stores the number of columns in the row
       unsigned long numCols{};
       // an array to store the row
       T *row;
   public:
   
       explicit Row(unsigned long cols = 0) : row(nullptr)
       {
           setSize(cols);
       }
   
       ~Row()
       {
           if(row)
           {
               delete[] row;
           }
       }
   
       Row(const Row &r) : row(0)
       {
           setSize(r.numCols);
           // Change to standard copy
           copy(&r.row[0], &r.row[numCols], row);
       }
   
   
       void setSize(unsigned long n)
       {
           if(row)
           {
               delete[] row;
           }
           if(n > 0)
           {
               row = new T[n];
           }
           else
           {
               row = 0;
           }
           numCols = n;
       }
   
       void resize(unsigned long n)
       {
           auto t = new T[n];
           for(unsigned long i = 0; i < numCols; i++)
           {
               t[i] = row[i];
           }
           delete[] row;
           row = move(t);
           numCols = n;
       }
   
       unsigned long size()
       {
           return numCols;
       }
   
       T &operator[](unsigned long column)
       {
           // assert(column<numCols);
           // check we are within bounds
   #ifdef DEBUG
           if(column < 0 || column >= numCols)
           {
               string err =
                       "ERROR_MAIN_013b: Tried to call an indices that was out of range of the row. Check row size definition. numCols: " +
                       to_string((long long) numCols) + " index: " + to_string((long long) column);
               throw out_of_range(err);
           }
   #endif
           column = column % numCols;
           return row[column];
       }
   
       Row &operator=(const Row &r)
       {
           setSize(r.numCols);
           for(unsigned long i = 0; i < numCols; i++)
           {
               row[i] = r.row[i];
           }
           return *this;
       }
   
       friend ostream &operator<<(ostream &os, const Row &r)
       {
           os << r.numCols << ",";
           for(unsigned long c = 0; c < r.numCols; c++)
           {
               os << r.row[c] << ",";
           }
           return os;
       }
   
       friend istream &operator>>(istream &is, Row &r)
       {
           char delim;
           int n;
           is >> n;
           r.setSize(n);
           is >> delim;
           for(unsigned long c = 0; c < r.numCols; c++)
           {
               is >> r.row[c];
               is >> delim;
           }
           return is;
       }
   };
   
   
   template<class T>
   class Matrix
   {
   
   protected:
   
       // number of rows and columns
       unsigned long numCols{}, numRows{};
       // a matrix is an array of rows
       Row<T> *matrix;
   
   public:
   
       explicit Matrix(unsigned long rows = 0, unsigned long cols = 0) : matrix(null)
       {
           SetSize(rows, cols);
       }
   
       Matrix(const Matrix &m) : matrix(null)
       {
           SetSize(m.numRows, m.numCols);
           copy(&m.matrix[0][0], &m.matrix[numRows][numCols], matrix);
       }
   
       ~Matrix()
       {
           if(matrix)
           {
               delete[] matrix;
           }
       }
   
       void SetSize(unsigned long rows, unsigned long cols)
       {
           if(matrix)
           {
               delete[]matrix;
           }
           if(cols > 0 && rows > 0)
           {
               matrix = new Row<T>[rows];
               for(unsigned long i = 0; i < rows; i++)
               {
                   matrix[i].setSize(cols);
               }
           }
           else
           {
               matrix = null;
           }
           numCols = cols;
           numRows = rows;
       }
   
       unsigned long GetCols() const
       {
           return numCols;
       }
   
       unsigned long GetRows() const
       {
           return numRows;
       }
   
       Row<T> &operator[](unsigned long index)
       {
   #ifdef DEBUG
           if(index < 0 || index >= numRows)
           {
               string err =
                       "ERROR_MAIN_013: Tried to call an indices that was out of range of the matrix. Check matrix size definition. numRows: " +
                       to_string((long long) numRows) + " index: " + to_string((long long) index);
               throw out_of_range(err);
           }
   #endif
           index = index % numRows;
           return matrix[index];
       }
   
       Matrix &operator=(const Matrix &m)
       {
           SetSize(m.numRows, m.numCols);
           for(unsigned long r = 0; r < numRows; r++)
           {
               matrix[r] = Row<T>(m.matrix[r]);
           }
           return *this;
       }
   
   
       const Matrix operator+(const Matrix &m)
       {
           //Since addition creates a new matrix, we don't want to return a reference, but an actual matrix object.
           unsigned long newnumcols, newnumrows;
           if(numCols > m.numCols)
           {
               newnumcols = m.numCols;
           }
           else
           {
               newnumcols = numCols;
           }
           if(numRows > m.numRows)
           {
               newnumrows = m.numRows;
           }
           else
           {
               newnumrows = numRows;
           }
   
           Matrix result(newnumrows, newnumcols);
           for(unsigned long r = 0; r < newnumrows; r++)
           {
               for(unsigned long c = 0; c < newnumcols; c++)
               {
                   result[r][c] = matrix[r][c] + m.matrix[r][c];
               }
           }
           return result;
       }
   
       const Matrix operator-(const Matrix &m)
       {
           unsigned long newnumcols, newnumrows;
           if(numCols > m.numCols)
           {
               newnumcols = m.numCols;
           }
           else
           {
               newnumcols = numCols;
           }
           if(numRows > m.numRows)
           {
               newnumrows = m.numRows;
           }
           else
           {
               newnumrows = numRows;
           }
           Matrix result(newnumrows, newnumcols);
           for(unsigned long r = 0; r < newnumrows; r++)
           {
               for(unsigned long c = 0; c < newnumcols; c++)
               {
                   result[r][c] = matrix[r][c] - m.matrix[r][c];
               }
           }
           return result;
       }
   
       Matrix &operator+=(const Matrix &m)
       {
           unsigned long newnumcols, newnumrows;
           if(numCols > m.numCols)
           {
               newnumcols = m.numCols;
           }
           else
           {
               newnumcols = numCols;
           }
           if(numRows > m.numRows)
           {
               newnumrows = m.numRows;
           }
           else
           {
               newnumrows = numRows;
           }
           for(unsigned long r = 0; r < newnumrows; r++)
           {
               for(unsigned long c = 0; c < newnumcols; c++)
               {
                   matrix[r][c] += m.matrix[r][c];
               }
           }
           return *this;
       }
   
   
       Matrix &operator-=(const Matrix &m)
       {
           unsigned long newnumcols, newnumrows;
           if(numCols > m.numCols)
           {
               newnumcols = m.numCols;
           }
           else
           {
               newnumcols = numCols;
           }
           if(numRows > m.numRows)
           {
               newnumrows = m.numRows;
           }
           else
           {
               newnumrows = numRows;
           }
           for(unsigned long r = 0; r < newnumrows; r++)
           {
               for(unsigned long c = 0; c < newnumcols; c++)
               {
                   matrix[r][c] -= m.matrix[r][c];
               }
           }
           return *this;
       }
   
       const Matrix operator*(const double s)
       {
           Matrix result(numRows, numCols);
           for(unsigned long r = 0; r < numRows; r++)
           {
               for(unsigned long c = 0; c < numCols; c++)
               {
                   result[r][c] = matrix[r][c] * s;
               }
           }
           return result;
       }
   
   
       const Matrix operator*(Matrix &m)
       {
           unsigned long newnumcols;
           if(numCols > m.numRows)
           {
               newnumcols = m.numRows;
           }
           else
           {
               newnumcols = numCols;
           }
   
           Matrix result(numRows, m.numCols);
           for(unsigned long r = 0; r < numRows; r++)
           {
               for(unsigned long c = 0; c < m.numCols; c++)
               {
                   for(unsigned long i = 0; i < newnumcols; i++)
                   {
                       result[r][c] += matrix[r][i] * m[i][c];
                   }
               }
           }
           return result;
       }
   
       friend ostream &operator<<(ostream &os, const Matrix &m)
       {
           for(unsigned long r = 0; r < m.numRows; r++)
           {
               for(unsigned long c = 0; c < m.numCols; c++)
               {
                   os << m.matrix[r][c] << ",";
               }
               os << "\n";
           }
           return os;
       }
   
       friend istream &operator>>(istream &is, Matrix &m)
       {
           char delim;
           for(unsigned long r = 0; r < m.numRows; r++)
           {
               for(unsigned long c = 0; c < m.numCols; c++)
               {
                   is >> m.matrix[r][c];
                   is >> delim;
               }
           }
           return is;
       }
   
       void setValue(const unsigned long &x, const unsigned long &y, const char *value)
       {
           matrix[y][x] = static_cast<T>(*value);
       }
   
       void import(const string &filename)
       {
           if(filename.find(".csv") != string::npos)
           {
               importCsv(filename);
           }
   #ifdef with_gdal
           else if(filename.find(".tif") != string::npos)
           {
               importTif(filename);
               return;
           }
   #endif
           string s = "Type detection failed for " + filename + ". Check filename is correct.";
           throw runtime_error(s);
       }
   
   #ifdef with_gdal
       void importTif(const string &filename)
       {
           stringstream ss;
           ss << "Importing " << filename << " " << flush;
           writeInfo(ss.str());
           GDALDataset *poDataset;
           GDALAllRegister();
           poDataset = (GDALDataset *) GDALOpen(filename.c_str(), GA_ReadOnly);
           if(poDataset == nullptr)
           {
               string s = "File " + filename + " not found.";
               throw runtime_error(s);
           }
           GDALRasterBand *poBand;
           int nBlockXSize, nBlockYSize;
           // Import the raster band 1
           poBand = poDataset->GetRasterBand(1);
           nBlockXSize = poDataset->GetRasterXSize();
           nBlockYSize = poDataset->GetRasterYSize();
           double noDataValue;
           try
           {
               noDataValue = poBand->GetNoDataValue();
           }
           catch(out_of_range)
           {
               noDataValue = 0;
           }
           // Check sizes
           if((numCols != (unsigned long) nBlockXSize || numRows != (unsigned long) nBlockYSize) || numCols == 0 ||
              numRows == 0)
           {
               stringstream ss;
               ss << "Raster data size does not match inputted dimensions for " << filename << ". Using raster sizes."
                    << endl;
               ss << "Old dimensions: " << numCols << ", " << numRows << endl;
               ss << "New dimensions: " << nBlockXSize << ", " << nBlockYSize << endl;
               writeWarning(ss.str());
               SetSize(static_cast<unsigned long>(nBlockYSize), static_cast<unsigned long>(nBlockXSize));
           }
           // Check sizes match
           GDALDataType dt = poBand->GetRasterDataType();
           const char *dt_name = GDALGetDataTypeName(dt);
           CPLErr r;
           // Check the data types are support
           if(dt == 0 || dt > 7)
           {
               throw FatalException("Data type of " + string(dt_name) + "is not supported.");
           }
   #ifdef DEBUG
           if(sizeof(T) * 8 != gdal_data_sizes[dt])
           {
               stringstream ss;
               ss << "Object data size: " << sizeof(T) * 8 << endl;
               ss << "Tif data type: " << dt_name << ": " << gdal_data_sizes[dt] << " bytes" << endl;
               ss << "Tif data type does not match object data size in " << filename << endl;
               writeWarning(ss.str());
           }
   #endif
           // Just use the overloaded method for importing between types
           internalImport(filename, poBand, nBlockXSize, dt, r, noDataValue);
           GDALClose(poDataset);
           writeInfo("done!\n");
       }
   
       void internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                        GDALDataType dt, CPLErr &r, const double &ndv)
       {
           writeWarning("No type detected for matrix type. Attempting default importing (undefined behaviour).");
           defaultImport(filename, poBand, nBlockXSize, dt, r, ndv);
       }
   
       void defaultImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                          GDALDataType dt, CPLErr &r, const double &ndv)
       {
           unsigned int number_printed = 0;
           for(uint32_t j = 0; j < numRows; j++)
           {
               printNumberComplete(j, number_printed, filename);
               r = poBand->RasterIO(GF_Read, 0, j, nBlockXSize, 1, &matrix[j][0], nBlockXSize, 1, dt, 0, 0);
               checkRasterBandFailure(r);
               // Now convert the no data values to 0
               for(uint32_t i = 0; i < numCols; i++)
               {
                   if(matrix[j][i] == ndv)
                   {
                       matrix[j][i] = 0;
                   }
               }
           }
       }
   
       void importFromDoubleAndMakeBool(const string &filename, GDALRasterBand * poBand, int nBlockXSize,
                                      GDALDataType dt, CPLErr & r, const double & ndv)
       {
           unsigned int number_printed = 0;
           // create an empty row of type float
           double * t1;
           t1 = (double *) CPLMalloc(sizeof(double) * numCols);
           // importSpatialParameters the data a row at a time, using our template row.
           for(uint32_t j = 0; j < numRows; j++)
           {
               printNumberComplete(j, number_printed, filename);
               r = poBand->RasterIO(GF_Read, 0, j, nBlockXSize, 1, &t1[0], nBlockXSize, 1, GDT_Float64, 0, 0);
               checkRasterBandFailure(r);
               // now copy the data to our matrix, converting float to int. Round or floor...? hmm, floor?
               for(unsigned long i = 0; i < numCols; i++)
               {
                   if(t1[i] == ndv)
                   {
                       matrix[j][i] = false;
                   }
                   else
                   {
                       matrix[j][i] = t1[i] >= 0.5;
                   }
               }
           }
           CPLFree(t1);
       };
       template<typename T2> void importUsingBuffer(const string &filename, GDALRasterBand * poBand, int nBlockXSize,
                              GDALDataType dt, CPLErr & r, const double & ndv)
       {
           unsigned int number_printed = 0;
           // create an empty row of type float
           T2 * t1;
           t1 = (T2 *) CPLMalloc(sizeof(T2) * numCols);
           // importSpatialParameters the data a row at a time, using our template row.
           for(uint32_t j = 0; j < numRows; j++)
           {
               printNumberComplete(j, number_printed, filename);
               r = poBand->RasterIO(GF_Read, 0, j, nBlockXSize, 1, &t1[0], nBlockXSize, 1, dt, 0, 0);
               checkRasterBandFailure(r);
               // now copy the data to our matrix, converting float to int. Round or floor...? hmm, floor?
               for(unsigned long i = 0; i < numCols; i++)
               {
                   if(t1[i] == ndv)
                   {
                       matrix[j][i] = static_cast<T>(0);
                   }
                   else
                   {
                       matrix[j][i] = static_cast<T>(t1[i]);
                   }
               }
           }
           CPLFree(t1);
       };
   
       void printNumberComplete(const uint32_t &j, unsigned int & number_printed, const string & filename)
       {
           double dComplete = ((double) j / (double) numRows) * 20;
           if(number_printed < dComplete)
           {
               stringstream os;
               os << "\rImporting " << filename << " ";
               number_printed = 0;
               while(number_printed < dComplete)
               {
                   os << ".";
                   number_printed++;
               }
               os << flush;
               writeInfo(os.str());
           }
       }
   
       void checkRasterBandFailure(const CPLErr & r)
       {
           if(r == CE_Failure)
           {
               char *fmt = nullptr;
               CPLError(r, CPLGetLastErrorNo(), "%s\n", fmt);
               throw runtime_error("CPL error during tif importSpatialParameters: CE_Failure: " + string(fmt));
           }
       }
   
   #endif
   
   
   #ifdef use_csv
       void importCsv(const string &filename)
       {
           stringstream os;
           os  << "Importing " << filename << " " << flush;
           writeInfo(os.str());
           // LineReader option
           io::LineReader in(filename);
           // Keep track of whether we've printed to terminal or not.
           bool bPrint = false;
           // Initialies empty variable so that the setValue operator overloading works properly.
           unsigned int number_printed = 0;
           for(unsigned long i =0; i<numRows; i++)
           {
               char* line = in.next_line();
               if(line == nullptr)
               {
                   if(!bPrint)
                   {
                       cerr << "Input dimensions incorrect - read past end of file." << endl;
                       bPrint = true;
                   }
                   break;
               }
               else
               {
                   char *dToken;
                   dToken = strtok(line,",");
                   for(unsigned long j = 0; j<numCols; j++)
                   {
                       if(dToken == nullptr)
                       {
                           if(!bPrint)
                           {
                               cerr << "Input dimensions incorrect - read past end of file." << endl;
                               bPrint = true;
                           }
                           break;
                       }
                       else
                       {
                           // This function is overloaded to correctly determine the type of the template
                           setValue(j,i,dToken);
                           dToken = strtok(NULL,",");
                       }
                   }
                   // output the percentage complete
                   double dComplete = ((double)i/(double)numRows)*20;
                   if( number_printed < dComplete)
                   {
                       stringstream os;
                       os  << "\rImporting " << filename << " ";
                       number_printed = 0;
                       while(number_printed < dComplete)
                       {
                           os << ".";
                           number_printed ++;
                       }
                       os << flush;
                       writeInfo(os.str());
                   }
                   
               }
           }
           writeInfo("done!\n");
       }
   #endif
   #ifndef use_csv
   
       void importCsv(const string &filename)
       {
           stringstream os;
           os << "Importing" << filename << " " << flush;
           ifstream inputstream;
           inputstream.open(filename.c_str());
           unsigned long number_printed = 0;
           for(uint32_t j = 0; j < numRows; j++)
           {
               string line;
               getline(inputstream, line);
               istringstream iss(line);
               for(uint32_t i = 0; i < numCols; i++)
               {
                   char delim;
                   T val;
                   iss >> val >> delim;
                   matrix[j][i] = val;
               }
               double dComplete = ((double) j / (double) numRows) * 5;
               if(number_printed < dComplete)
               {
                   os << "\rImporting " << filename << " " << flush;
                   while(number_printed < dComplete)
                   {
                       os << ".";
                       number_printed++;
                   }
                   os << flush;
                   writeInfo(os.str());
   
               }
           }
           stringstream os2;
           os2 << "\rImporting" << filename << "..." << "done!" << "                          " << endl;
           inputstream.close();
           writeInfo(os2.str());
       }
   
   #endif
   };
   
   #ifdef with_gdal
   
   template<> inline void Matrix<bool>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                       GDALDataType dt, CPLErr &r, const double &ndv)
   {
       if(dt <=7)
       {
           // Then the tif file type is an int/byte
           // we can just import as it is
           importUsingBuffer<uint8_t>(filename, poBand, nBlockXSize, GDT_Byte, r, ndv);
       }
       else
       {
           // Conversion from double to boolean
           importFromDoubleAndMakeBool(filename, poBand, nBlockXSize, dt, r, ndv);
       }
   }
   template <>inline void Matrix<int8_t>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                      GDALDataType dt, CPLErr &r, const double &ndv)
   {
       importUsingBuffer<int16_t>(filename, poBand, nBlockXSize, GDT_Int16, r, ndv);
   }
   
   template <>inline void Matrix<uint8_t>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                      GDALDataType dt, CPLErr &r, const double &ndv)
   {
       defaultImport(filename, poBand, nBlockXSize, GDT_Byte, r, ndv);
   }
   
   template <>inline void Matrix<int16_t>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                                GDALDataType dt, CPLErr &r, const double &ndv)
   {
       defaultImport(filename, poBand, nBlockXSize, GDT_Int16, r, ndv);
   }
   template <>inline void Matrix<uint16_t>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                                GDALDataType dt, CPLErr &r, const double &ndv)
   {
       defaultImport(filename, poBand, nBlockXSize, GDT_UInt16, r, ndv);
   }
   template <>inline void Matrix<uint32_t>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                                 GDALDataType dt, CPLErr &r, const double &ndv)
   {
       defaultImport(filename, poBand, nBlockXSize, GDT_UInt32, r, ndv);
   }
   template <>inline void Matrix<int32_t>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                           GDALDataType dt, CPLErr &r, const double &ndv)
   {
       defaultImport(filename, poBand, nBlockXSize, GDT_Int32, r, ndv);
   }
   template <>inline void Matrix<float>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                                 GDALDataType dt, CPLErr &r, const double &ndv)
   {
       defaultImport(filename, poBand, nBlockXSize, GDT_Float32, r, ndv);
   }
   
   template <>inline void Matrix<double>::internalImport(const string &filename, GDALRasterBand *poBand, int nBlockXSize,
                                                                 GDALDataType dt, CPLErr &r, const double &ndv)
   {
       defaultImport(filename, poBand, nBlockXSize, GDT_Float64, r, ndv);
   }
   
   #endif // gdal
   #endif // MATRIX

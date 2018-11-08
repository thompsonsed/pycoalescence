
.. _program_listing_file_necsim_Map.h:

Program Listing for File Map.h
==============================

- Return to documentation for :ref:`file_necsim_Map.h`

.. code-block:: cpp

   // This file is part of necsim project which is released under MIT license.
   // See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details
   #ifndef MAP_H
   #define MAP_H
   #ifdef with_gdal
   
   #include <string>
   #include <cstring>
   #include <sstream>
   #include "Logger.h"
   #include <gdal_priv.h>
   #include <cpl_conv.h> // for CPLMalloc()
   #include <sstream>
   #include "Matrix.h"
   #include "Logger.h"
   #include "custom_exceptions.h"
   #include "cpl_custom_handler.h"
   
   using namespace std;
   #ifdef DEBUG
   #include "custom_exceptions.h"
   #endif // DEBUG
   
   template<class T>
   class Map : public virtual Matrix<T>
   {
   protected:
       GDALDataset *poDataset;
       GDALRasterBand *poBand;
       unsigned long blockXSize, blockYSize;
       double noDataValue;
       string filename;
       GDALDataType dt{};
       // Contains the error object to check for any gdal issues
       CPLErr cplErr{CE_None};
       double upper_left_x{}, upper_left_y{}, x_res{}, y_res{};
       using Matrix<T>::matrix;
       using Matrix<T>::numCols;
       using Matrix<T>::numRows;
   public:
       using Matrix<T>::setSize;
       using Matrix<T>::getCols;
       using Matrix<T>::getRows;
       using Matrix<T>::operator*;
       using Matrix<T>::operator+;
       using Matrix<T>::operator-;
       using Matrix<T>::operator-=;
       using Matrix<T>::operator+=;
       using Matrix<T>::operator[];
   
       Map() : Matrix<T>(0, 0)
       {
           GDALAllRegister();
           poDataset = nullptr;
           poBand = nullptr;
           filename = "";
           blockXSize = 0;
           blockYSize = 0;
           noDataValue = 0.0;
           CPLSetErrorHandler(cplNecsimCustomErrorHandler);
       }
   
       ~Map()
       {
           close();
       }
   
       void open(const string &filename_in)
       {
           if(!poDataset)
           {
               filename = filename_in;
               poDataset = (GDALDataset *) GDALOpen(filename.c_str(), GA_ReadOnly);
           }
           else
           {
               throw FatalException("File already open at " + filename);
           }
           if(!poDataset)
           {
               string s = "File " + filename + " not found.";
               throw runtime_error(s);
           }
       }
   
       void open()
       {
           open(filename);
       }
   
       bool isOpen()
       {
           return poDataset != nullptr;
       }
   
       void close()
       {
           if(poDataset)
           {
               GDALClose(poDataset);
   //          if(poDataset)
   //          {
   //              throw FatalException("poDataset not nullptr after closing, please report this bug.");
   //          }
               poDataset = nullptr;
               poBand = nullptr;
           }
       }
   
       void getRasterBand()
       {
           poBand = poDataset->GetRasterBand(1);
       }
   
       void getBlockSizes()
       {
           blockXSize = static_cast<unsigned long>(poDataset->GetRasterXSize());
           blockYSize = static_cast<unsigned long>(poDataset->GetRasterYSize());
       }
   
       void getMetaData()
       {
           try
           {
               int pbSuccess;
               noDataValue = poBand->GetNoDataValue(&pbSuccess);
               if(!pbSuccess)
               {
                   noDataValue = 0.0;
               }
           }
           catch(out_of_range &out_of_range1)
           {
               noDataValue = 0.0;
           }
           stringstream ss;
           ss << "No data value is: " << noDataValue << endl;
           writeInfo(ss.str());
           // Check sizes match
           dt = poBand->GetRasterDataType();
           double geoTransform[6];
           cplErr = poDataset->GetGeoTransform(geoTransform);
           if(cplErr >= CE_Warning)
           {
               CPLError(cplErr, 6, "No transform present in dataset for %s.", filename.c_str());
               CPLErrorReset();
           }
           upper_left_x = geoTransform[0];
           upper_left_y = geoTransform[3];
           x_res = geoTransform[1];
           y_res = -geoTransform[5];
   //      checkTifImportFailure();
   #ifdef DEBUG
           printMetaData();
   #endif // DEBUG
       }
   
   #ifdef DEBUG
       void printMetaData()
       {
           stringstream ss;
           const char *dt_name = GDALGetDataTypeName(dt);
           ss << "Filename: " << filename << endl;
           writeLog(10, ss.str());
           ss.str("");
           ss << "data type: " << dt << "(" << dt_name << ")" << endl;
           writeLog(10, ss.str());
           ss.str("");
           ss << "Geo-transform (ulx, uly, x res, y res): " << upper_left_x << ", " << upper_left_y << ", ";
           ss << x_res << ", " << y_res << ", " <<endl;
           writeLog(10, ss.str());
           ss.str("");
           ss << "No data value: " << noDataValue << endl;
           writeLog(10, ss.str());
   
       }
   #endif //DEBUG
   
       double getUpperLeftX()
       {
           return upper_left_x;
       }
   
       double getUpperLeftY()
       {
           return upper_left_y;
       }
   
       void import(const string &filename) override
       {
           if(!importTif(filename))
           {
               Matrix<T>::import(filename);
           }
       }
   
       bool importTif(const string &filename)
       {
   
           if(filename.find(".tif") != string::npos)
           {
               stringstream ss;
               ss << "Importing " << filename << " " << flush;
               writeInfo(ss.str());
               open(filename);
               getRasterBand();
               getBlockSizes();
               getMetaData();
               // If the sizes are 0 then use the raster sizes
               if(numCols == 0 || numRows == 0)
               {
                   setSize(blockYSize, blockXSize);
               }
               // Check sizes
               if((numCols != blockXSize || numRows != blockYSize) || numCols == 0 ||
                  numRows == 0)
               {
                   stringstream stringstream1;
                   stringstream1 << "Raster data size does not match inputted dimensions for " << filename
                                 << ". Using raster sizes."
                                 << endl;
                   stringstream1 << "Old dimensions: " << numCols << ", " << numRows << endl;
                   stringstream1 << "New dimensions: " << blockXSize << ", " << blockYSize << endl;
                   writeWarning(stringstream1.str());
                   setSize(blockYSize, blockXSize);
               }
               // Check the data types are support
               const char *dt_name = GDALGetDataTypeName(dt);
               if(dt == 0 || dt > 7)
               {
                   throw FatalException("Data type of " + string(dt_name) + " is not supported.");
               }
   #ifdef DEBUG
               if(sizeof(T) * 8 != gdal_data_sizes[dt])
               {
                   stringstream ss2;
                   ss2 << "Object data size: " << sizeof(T) * 8 << endl;
                   ss2 << "Tif data type: " << dt_name << ": " << gdal_data_sizes[dt] << " bytes" << endl;
                   ss2 << "Tif data type does not match object data size in " << filename << endl;
                   writeWarning(ss2.str());
               }
   #endif
               // Just use the overloaded method for importing between types
               internalImport();
               writeInfo("done!\n");
               return true;
           }
           return false;
       }
   
       bool openOffsetMap(Map &offset_map)
       {
           bool opened_here = false;
           if(!offset_map.isOpen())
           {
               opened_here = true;
               offset_map.open();
           }
           offset_map.getRasterBand();
           offset_map.getMetaData();
           return opened_here;
       }
   
       void closeOffsetMap(Map &offset_map, const bool &opened_here)
       {
           if(opened_here)
           {
               offset_map.close();
           }
       }
   
       void calculateOffset(Map &offset_map, long &offset_x, long &offset_y)
       {
           auto opened_here = openOffsetMap(offset_map);
           offset_x = static_cast<long>(round((upper_left_x - offset_map.upper_left_x) / x_res));
           offset_y = static_cast<long>(round((offset_map.upper_left_y - upper_left_y )/ y_res));
           closeOffsetMap(offset_map, opened_here);
       }
   
       unsigned long roundedScale(Map &offset_map)
       {
           auto opened_here = openOffsetMap(offset_map);
           closeOffsetMap(offset_map, opened_here);
           return static_cast<unsigned long>(floor(offset_map.x_res / x_res));
       }
   
       void internalImport()
       {
           writeWarning("No type detected for Map type. Attempting default importing (potentially undefined behaviour).");
           defaultImport();
       }
   
       void defaultImport()
       {
           unsigned int number_printed = 0;
           for(uint32_t j = 0; j < numRows; j++)
           {
               printNumberComplete(j, number_printed);
               cplErr = poBand->RasterIO(GF_Read, 0, j, static_cast<int>(blockXSize), 1, &matrix[j][0],
                                         static_cast<int>(blockXSize), 1, dt, 0, 0);
               checkTifImportFailure();
               // Now convert the no data values to 0
               for(uint32_t i = 0; i < numCols; i++)
               {
                   if(matrix[j][i] == noDataValue)
                   {
                       matrix[j][i] = 0;
                   }
               }
           }
       }
   
       void importFromDoubleAndMakeBool()
       {
           unsigned int number_printed = 0;
           // create an empty row of type float
           double *t1;
           t1 = (double *) CPLMalloc(sizeof(double) * numCols);
           // import the data a row at a time, using our template row.
           for(uint32_t j = 0; j < numRows; j++)
           {
               printNumberComplete(j, number_printed);
               cplErr = poBand->RasterIO(GF_Read, 0, j, static_cast<int>(blockXSize), 1, &t1[0],
                                         static_cast<int>(blockXSize), 1, GDT_Float64, 0, 0);
               checkTifImportFailure();
               // now copy the data to our Map, converting float to int. Round or floor...? hmm, floor?
               for(unsigned long i = 0; i < numCols; i++)
               {
                   if(t1[i] == noDataValue)
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
       }
   
       template<typename T2>
       void importUsingBuffer(GDALDataType dt_buff)
       {
           unsigned int number_printed = 0;
           // create an empty row of type float
           T2 *t1;
           t1 = (T2 *) CPLMalloc(sizeof(T2) * numCols);
           // import the data a row at a time, using our template row.
           for(uint32_t j = 0; j < numRows; j++)
           {
               printNumberComplete(j, number_printed);
               cplErr = poBand->RasterIO(GF_Read, 0, j, static_cast<int>(blockXSize), 1, &t1[0],
                                         static_cast<int>(blockXSize), 1, dt_buff, 0, 0);
               checkTifImportFailure();
               // now copy the data to our Map, converting float to int. Round or floor...? hmm, floor?
               for(unsigned long i = 0; i < numCols; i++)
               {
                   if(t1[i] == noDataValue)
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
       }
   
       void printNumberComplete(const uint32_t &j, unsigned int &number_printed)
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
   
       void checkTifImportFailure()
       {
           if(cplErr >= CE_Warning)
           {
               CPLError(cplErr, 3, "CPL error thrown during import of %s\n", filename.c_str());
               CPLErrorReset();
           }
       }
   
       friend ostream &operator>>(ostream &os, const Map &m)
       {
           return Matrix<T>::writeOut(os, m);
       }
   
       friend istream &operator<<(istream &is, Map &m)
       {
           return Matrix<T>::readIn(is, m);
       }
   
       Map &operator=(const Map &m)
       {
           Matrix<T>::operator=(m);
           this->poDataset = m.poDataset;
           this->poBand = m.poBand;
           this->blockXSize = m.blockXSize;
           this->blockYSize = m.blockYSize;
           this->noDataValue = m.noDataValue;
           this->filename = m.filename;
           this->dt = m.dt;
           this->cplErr = m.cplErr;
           this->upper_left_x = m.upper_left_x;
           this->upper_left_y = m.upper_left_y;
           this->x_res = m.x_res;
           this->y_res = m.y_res;
           return *this;
       }
   
   };
   
   template<>
   inline void Map<bool>::internalImport()
   {
       if(dt <= 7)
       {
           // Then the tif file type is an int/byte
           // we can just import as it is
           importUsingBuffer<uint8_t>(GDT_Byte);
       }
       else
       {
           // Conversion from double to boolean
           importFromDoubleAndMakeBool();
       }
   }
   
   template<>
   inline void Map<int8_t>::internalImport()
   {
       importUsingBuffer<int16_t>(GDT_Int16);
   }
   
   template<>
   inline void Map<uint8_t>::internalImport()
   {
       dt = GDT_Byte;
       defaultImport();
   }
   
   template<>
   inline void Map<int16_t>::internalImport()
   {
       dt = GDT_Int16;
       defaultImport();
   }
   
   template<>
   inline void Map<uint16_t>::internalImport()
   {
       dt = GDT_UInt16;
       defaultImport();
   }
   
   template<>
   inline void Map<int32_t>::internalImport()
   {
       dt = GDT_Int32;
       defaultImport();
   }
   
   template<>
   inline void Map<uint32_t>::internalImport()
   {
       dt = GDT_UInt32;
       defaultImport();
   }
   
   template<>
   inline void Map<float>::internalImport()
   {
       dt = GDT_Float32;
       defaultImport();
   }
   
   template<>
   inline void Map<double>::internalImport()
   {
       dt = GDT_Float64;
       defaultImport();
   }
   
   #endif // with_gdal
   #endif //MAP_H

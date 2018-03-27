
.. _program_listing_file_necsim_Matrix.h:

Program Listing for File Matrix.h
=================================

- Return to documentation for :ref:`file_necsim_Matrix.h`

.. code-block:: cpp

   
   #ifndef MATRIX
   #define MATRIX
   #define null 0
   #include <cstdio>
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
           setSize(rows, cols);
       }
   
       Matrix(const Matrix &m) : matrix(null)
       {
           setSize(m.numRows, m.numCols);
           copy(&m.matrix[0][0], &m.matrix[numRows][numCols], matrix);
       }
   
       ~Matrix()
       {
           if(matrix)
           {
               delete[] matrix;
           }
       }
   
       void setSize(unsigned long rows, unsigned long cols)
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
   
       unsigned long getCols() const
       {
           return numCols;
       }
   
       unsigned long getRows() const
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
           setSize(m.numRows, m.numCols);
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
   
       friend ostream& writeOut(ostream &os, const Matrix &m)
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
   
       friend istream& readIn(istream & is, Matrix &m)
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
       }
   
       friend ostream &operator<<(ostream &os, const Matrix &m)
       {
           return writeOut(os, m);
       }
   
       friend istream &operator>>(istream &is, Matrix &m)
       {
           return readIn(is, m);
       }
   
       void setValue(const unsigned long &x, const unsigned long &y, const char *value)
       {
           matrix[y][x] = static_cast<T>(*value);
       }
   
       virtual void import(const string &filename)
       {
           if(!importCsv(filename))
           {
               string s = "Type detection failed for " + filename + ". Check filename is correct.";
               throw runtime_error(s);
           }
       }
   
   #ifdef use_csv
       bool importCsv(const string &filename)
       {
       if(filename.find(".csv") != string::npos)
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
                           writeError("Input dimensions incorrect - read past end of file.");
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
                               writeError("Input dimensions incorrect - read past end of file.");
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
               return true;
           }
           return false;
       }
   #endif
   #ifndef use_csv
   
       bool importCsv(const string &filename)
       {
           if(filename.find(".csv") != string::npos)
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
               return true;
           }
           return false;
       }
   
   #endif // use_csv
   };
   
   
   #endif // MATRIX

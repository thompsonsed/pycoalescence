#include <UnitTest++/UnitTest++.h>
//#define UNIT_TEST_PP_SRC_DIR "/usr/local/include/UnitTest++"
#include <stdexcept>
#include <stdio.h>
#include <iostream>
#include <sstream>
#include <iomanip>
#include <cmath>
#include <string>
#include <cstring>
#include "../Matrix.h"
#include "../ConfigFileParser.h"
//#include "../Fattaildeviate.h"
#include "../Tree.h"
#include "../Treenode.h"
#include "../Map.h"
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//
// To add a test, simply put the following code in the a .cpp file of your choice:
//
// =================================
// Simple Test
// =================================
//
//  TEST(YourTestName)
//  {
//  }
//
// The TEST macro contains enough machinery to turn this slightly odd-looking syntax into legal C++, and automatically register the test in a global list. 
// This test list forms the basis of what is executed by RunAllTests().
//
// If you want to re-use a set of test data for more than one test, or provide setup/teardown for tests, 
// you can use the TEST_FIXTURE macro instead. The macro requires that you pass it a class name that it will instantiate, so any setup and teardown code should be in its constructor and destructor.
//
//  struct SomeFixture
//  {
//    SomeFixture() { /* some setup */ }
//    ~SomeFixture() { /* some teardown */ }
//
//    int testData;
//  };
// 
//  TEST_FIXTURE(SomeFixture, YourTestName)
//  {
//    int temp = testData;
//  }
//
// =================================
// Test Suites
// =================================
// 
// Tests can be grouped into suites, using the SUITE macro. A suite serves as a namespace for test names, so that the same test name can be used in two difference contexts.
//
//  SUITE(YourSuiteName)
//  {
//    TEST(YourTestName)
//    {
//    }
//
//    TEST(YourOtherTestName)
//    {
//    }
//  }
//
// This will place the tests into a C++ namespace called YourSuiteName, and make the suite name available to UnitTest++. 
// RunAllTests() can be called for a specific suite name, so you can use this to build named groups of tests to be run together.
// Note how members of the fixture are used as if they are a part of the test, since the macro-generated test class derives from the provided fixture class.
//
//
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

SUITE(MatrixSuite)
{
	class TestMatrix : public Matrix<int>
	{
	public:
		Matrix<int> matrix;
		Matrix<int> matrix_compare;
		TestMatrix()
		{
			matrix.SetSize(20,20);
			matrix_compare.SetSize(20,20);
			unsigned int ref = 0;
			for(unsigned int i = 0; i < 20; i++)
			{
				for( unsigned int j = 0 ; j < 20; j++)
				{
					matrix_compare[j][i] = ref*2;
					matrix[j][i] = ref;
					ref ++;
				}
			}
		}
	};
	
	TEST_FIXTURE(TestMatrix, MatrixPass1)
	{
		CHECK_EQUAL(0, matrix[0][0]);
		CHECK_EQUAL(19, matrix[19][0]);
		CHECK_EQUAL(20*20-1, matrix[19][19]);
	}
	TEST_FIXTURE(TestMatrix, MatrixThrow1)
	{
		CHECK_THROW(matrix[-1][0], out_of_range);
		CHECK_THROW(matrix[21][0], out_of_range);
		CHECK_THROW(matrix[0][-1], out_of_range);
		CHECK_THROW(matrix[0][21], out_of_range);
	}
	
	TEST_FIXTURE(TestMatrix, MatrixPass2)
	{
		matrix = matrix*2;
		for(unsigned int i = 0; i < 20 ; i ++ )
		{
			for( unsigned int j = 0; j < 20 ; j ++ )
			{
				CHECK_EQUAL(matrix[j][i], matrix_compare[j][i]);
			}
		}
	}
	// TODO complete unit testing of matrix remainders
	// TODO test import functions
	// TODO test read in/write out functions
}

SUITE(ConfigSuite)
{
	class TestConfig
	{
	public:
		ConfigOption c;
		ConfigOption f;
		TestConfig()
		{
			string conf_file1 = "../TestFiles/ConfTest1.txt";
			string conf_file2 = "../TestFiles/ConfTest2.txt";
			c.setConfig(conf_file1, true, true);
			f.setConfig(conf_file2, true, true);
			c.parseConfig();
			
		}
	};
	TEST_FIXTURE(TestConfig, ConfigPass1)
	{
		CHECK_EQUAL("val1.1", c.getSectionOptions("key1","ref1.1"));
		CHECK_EQUAL("val1.2", c.getSectionOptions("key2","ref1.2"));
	}
	
	TEST_FIXTURE(TestConfig, ConfigFail1)
	{
		CHECK_THROW(f.parseConfig(), Config_Exception);
		CHECK_EQUAL("null", c.getSectionOptions("key1","refnull"));
		CHECK_EQUAL("null", c.getSectionOptions("keynull","ref1.1"));
	}
}

SUITE(RandNumSuite)
{
	class TestNR
	{
	public:
		NRrand NR;
		TestNR()
		{
			NR.setSeed(1);
		}
	};
	
	TEST_FIXTURE(TestNR, NRPass1)
	{
		CHECK_EQUAL(0.285380899094686113492969, NR.d01());
		CHECK_EQUAL(10, NR.i0(10));
	}
	TEST_FIXTURE(TestNR, NormalDistributionPass)
	{
		// Perform 1000 draws from the standard normal random number generator, and then calculate the mean and standard deviation
		vector<double> res;
		for(unsigned i = 0; i < 100000; i ++ )
		{
			res.push_back(NR.norm());
		}
		double mean = 0;
		double stdev = 0;
		for(unsigned i = 0; i < res.size(); i++)
		{
			mean += res[i];
		}
		mean /= 100000;
		for(unsigned i = 0; i < res.size(); i ++)
		{
			stdev += pow((res[i]-mean),2.0);
			
		}
		stdev /= 100000;
		stdev = pow(stdev, 0.5);
		CHECK_CLOSE(0, mean, 0.01);
		CHECK_CLOSE(1, stdev, 0.01);
		
	}
}

// Decision made that tree cannot contain unit tests as it contains too many dependencies to test individual modules.
// This is a problem with the development of the program structure, but cannot be fixed easily now.

// Map test
SUITE(MapSuite)
{
	class MapTest
	{
	public:
		SimParameters mvars;
		Map m;
		Datamask dm;
		MapTest()
		{
			// Generate the mapvar options.
			mvars.deme = 10;
			mvars.deme_sample = 1;
			mvars.dispersal_relative_cost = 1;
			mvars.pristinecoarsemapfile = "null";
			mvars.pristinefinemapfile = "null";
			mvars.coarsemapfile  = "null";
			mvars.finemapfile = "null";
			mvars.pristinefinemapfile = "null";
			mvars.varcoarsemapscale = 10;
			mvars.varcoarsemapxoffset = 0;
			mvars.varcoarsemapyoffset = 0;
			mvars.varfinemapxoffset = 0;
			mvars.varfinemapyoffset = 0;
			mvars.vargridxsize = 100;
			mvars.vargridysize = 100;
			mvars.varfinemapxsize = 100;
			mvars.varfinemapysize = 100;
			mvars.varcoarsemapxsize = 150;
			mvars.varcoarsemapysize = 150;
			mvars.samplemaskfile = "null";
			dm.importDatamask(mvars);
			
			
		}
		
		void setSize(unsigned int n, double sample)
		{
			mvars.deme_sample = sample;
			mvars.vargridxsize = n;
			mvars.vargridysize = n;
			mvars.varfinemapxsize = n;
			mvars.varfinemapysize = n;
		}
		
		void calculateMaps()
		{
			m.setDims(mvars);
			m.calcFineMap();
			m.calcCoarseMap();
			m.calcPristineCoarseMap();
			m.calcPristineFineMap();
			m.calcOffset();
			
		}
	};
	
	TEST_FIXTURE(MapTest, MapTestPass1)
	{
		setSize(100, 10);
		calculateMaps();
		unsigned int ic = m.getInitialCount(1.0,dm);
		CHECK_EQUAL(100000, ic);
		m.clearMap();
		setSize(100, 10);
		calculateMaps();
		ic = m.getInitialCount(0.5,dm);
		CHECK_EQUAL(50000, ic);
	}
	
	TEST_FIXTURE(MapTest, MapTestPass2)
	{
//		os << "start2" << endl;
		setSize(100, 10);
		calculateMaps();
		CHECK_EQUAL(10, m.getVal(0,0,0,0,0));
		CHECK_EQUAL(0, m.getVal(10, 10, -1 , 0 , 0));
		CHECK_EQUAL(0, m.getVal(10, 10, 0 , -1 , 0));
		CHECK_EQUAL(0, m.getVal(10, 10, -1 , -1 , 0));
		CHECK_EQUAL(true, m.checkFine(0,0,0,0));
		CHECK_EQUAL(false, m.checkFine(1,1,1,0));
		CHECK_EQUAL(true, m.checkFine(99,99,0,0));
	}
	TEST_FIXTURE(MapTest, MapTestFail1)
	{
//		os << "start3" << endl;
		setSize(100,10);
		calculateMaps();
		CHECK_THROW(m.getVal(101, 101, 0 , 0 , 0), out_of_range);
		CHECK_THROW(m.getVal(101, 101, -1 , -1 , 0), out_of_range);
		CHECK_THROW(m.checkFine(101,101,0,0), out_of_range);
		CHECK_THROW(m.checkFine(101,101,0,0), out_of_range);
	}
	
}
TEST(Testytest)
{
	CHECK_EQUAL(1,1);
}
// run all tests
int main(int argc, char **argv)
{
	return UnitTest::RunAllTests();
}

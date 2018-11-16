
.. _program_listing_file_necsim_Community.h:

Program Listing for File Community.h
====================================

|exhale_lsh| :ref:`Return to documentation for file <file_necsim_Community.h>` (``necsim/Community.h``)

.. |exhale_lsh| unicode:: U+021B0 .. UPWARDS ARROW WITH TIP LEFTWARDS

.. code-block:: cpp

   //This file is part of necsim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef TREELIST
   #define TREELIST
   
   #include <cmath>
   #include <sqlite3.h>
   #include <cstring>
   #include <stdexcept>
   #include <string>
   # include <boost/filesystem.hpp>
   #include <boost/lexical_cast.hpp>
   #include <set>
   #include <utility>
   #include <memory>
   
   #ifdef WIN_INSTALL
   #include <windows.h>
   #define sleep Sleep
   #endif
   
   #include "TreeNode.h"
   #include "Matrix.h"
   #include "DataMask.h"
   #include "parameters.h"
   #include "SpecSimParameters.h"
   
   using namespace std;
   using std::string;
   
   bool checkSpeciation(const long double &random_number, const long double &speciation_rate,
                        const unsigned long &no_generations);
   
   struct Fragment
   {
       // the name for the fragment (for reference purposes)
       string name;
       // coordinates for the extremes of the site
       long x_east, x_west, y_north, y_south;
       // the number of lineages in the fragment.
       unsigned long num;
       double area;
   };
   
   class Samplematrix : public DataMask
   {
   private:
       bool bIsNull;
       bool bIsFragment;
       Fragment fragment;
   public:
       Samplematrix();
   
   //  /**
   //   * @brief Returns the value at the x,y position.
   //   * This is used for testing purposes only.
   //   * @param xval the x coordinate.
   //   * @param yval the y coordinate
   //   * @param xwrap the x wrapping
   //   * @param ywrap the y wrapping
   //   * @return the value at x,y.
   //   */
       bool getTestVal(unsigned long xval, unsigned long yval, long xwrap, long ywrap);
   
       bool getMaskVal(unsigned long x1, unsigned long y1, long x_wrap, long y_wrap);
   
       void setFragment(Fragment &fragment_in);
   
       void removeFragment();
   };
   
   class Community
   {
   protected:
       bool in_mem; // boolean for whether the database is in memory or not.
       bool database_set; // boolean for whether the database has been set already.
       sqlite3 *database; // stores the in-memory database connection.
       bool bSqlConnection; // true if the data connection has been established.
       shared_ptr<vector<TreeNode>> nodes; // in older versions this was called species_id_list. Changed to avoid confusion with the built-in class.
       shared_ptr<vector<unsigned long>> species_abundances;
       unsigned long iSpecies;
       bool has_imported_samplemask; // checks whether the samplemask has already been imported.
       bool has_imported_data; // checks whether the main sim data has been imported.
       Samplematrix samplemask; // the samplemask object for defining the areas we want to sample from.
       vector<Fragment> fragments; // a vector of fragments for storing each fragment's coordinates.
       shared_ptr<CommunityParameters> current_community_parameters;
       shared_ptr<MetacommunityParameters> current_metacommunity_parameters;
       // the minimum speciation rate the original simulation was run with (this is read from the database SIMULATION_PARAMETERS table)
       long double min_spec_rate;
       // The dimensions of the sample grid size.
       unsigned long grid_x_size, grid_y_size;
       // The dimensions of the original sample map file
       unsigned long samplemask_x_size, samplemask_y_size, samplemask_x_offset, samplemask_y_offset;
       // Vector containing past speciation rates
       CommunitiesArray past_communities;
       MetacommunitiesArray past_metacommunities;
       // Protracted speciation current_metacommunity_parameters
       bool protracted;
       double min_speciation_gen, max_speciation_gen;
       ProtractedSpeciationParameters applied_protracted_parameters;
       unsigned long max_species_id, max_fragment_id, max_locations_id;
       // Does not need to be stored during simulation pause
       shared_ptr<SpecSimParameters> spec_sim_parameters;
   public:
   
       explicit Community(shared_ptr<vector<TreeNode>> r) : in_mem(false), database_set(false), database(nullptr),
                                                         bSqlConnection(false), nodes(std::move(r)),
                                                         species_abundances(make_shared<vector<unsigned long>>()),
                                                         iSpecies(0), has_imported_samplemask(false),
                                                         has_imported_data(false), samplemask(), fragments(),
                                                         current_community_parameters(make_shared<CommunityParameters>()),
                                                         current_metacommunity_parameters(
                                                                 make_shared<MetacommunityParameters>()),
                                                         min_spec_rate(0.0),
                                                         grid_x_size(0), grid_y_size(0), samplemask_x_size(0),
                                                         samplemask_y_size(0), samplemask_x_offset(0),
                                                         samplemask_y_offset(0), past_communities(),
                                                         past_metacommunities(), protracted(false),
                                                         min_speciation_gen(0.0), max_speciation_gen(0.0),
                                                         applied_protracted_parameters(), max_species_id(0),
                                                         max_fragment_id(0), max_locations_id(0),
                                                         spec_sim_parameters(make_shared<SpecSimParameters>())
       {
   
       }
   
       Community() : Community(make_shared<vector<TreeNode>>())
       {
       }
   
       virtual ~Community()
       {
           nodes.reset();
           sqlite3_close(database);
       }
   
       void setList(shared_ptr<vector<TreeNode>> l);
   
       void setDatabase(sqlite3 *dbin);
   
       bool hasImportedData();
   
       long double getMinimumSpeciation();
   
       void importSamplemask(string sSamplemask);
   
       unsigned long countSpecies();
   
       unsigned long calcSpecies();
   
       virtual void addSpecies(unsigned long &species_count, TreeNode *treenode, set<unsigned long> &species_list);
   
       void calcSpeciesAbundance();
   
       virtual void resetTree();
   
       void detectDimensions(string db);
   
       void openSqlConnection(string inputfile);
   
       void closeSqlConnection();
   
       void setInternalDatabase();
   
       void internalOption();
   
       void importData(string inputfile);
   
       void setSimParameters(shared_ptr<SimParameters> sim_parameters);
   
       void importSimParameters(string file);
   
       void forceSimCompleteParameter();
   
       bool isSetDatabase();
   
       void getMaxSpeciesAbundancesID();
   
       shared_ptr<vector<unsigned long>> getCumulativeAbundances();
   
       shared_ptr<vector<unsigned long>> getRowOut();
   
       unsigned long getSpeciesNumber();
   
       void getMaxFragmentAbundancesID();
   
       void getMaxSpeciesLocationsID();
   
       void setProtractedParameters(const ProtractedSpeciationParameters &protracted_params);
   
       void overrideProtractedParameters(const ProtractedSpeciationParameters &protracted_params);
   
       void setProtracted(bool protracted_in);
   
       void createDatabase();
   
       void generateCoalescenceTree();
   
       void outputSpeciesAbundances();
   
       bool checkCalculationsPerformed(const long double &speciation_rate, const double &time, const bool &fragments,
                                       const MetacommunityParameters &metacomm_parameters,
                                       const ProtractedSpeciationParameters &proc_parameters);
   
       void addCalculationPerformed(const long double &speciation_rate, const double &time, const bool &fragments,
                                    const MetacommunityParameters &metacomm_parameters,
                                    const ProtractedSpeciationParameters &protracted_parameters);
   
       void createFragmentDatabase(const Fragment &f);
   
       void exportDatabase();
   
       bool checkSpeciesLocationsReference();
   
       bool checkSpeciesAbundancesReference();
   
       void recordSpatial();
   
       void calcFragments(string fragment_file);
   
       void applyFragments();
   
       void getPreviousCalcs();
   
       vector<unsigned long> getUniqueCommunityRefs();
   
       vector<unsigned long> getUniqueMetacommunityRefs();
   
       void writeNewCommunityParameters();
   
       void writeNewMetacommunityParameters();
   
       void createSpeciesList();
   
       void deleteSpeciesList();
   
       void writeSpeciesList(const unsigned long &enddata);
   
       void updateCommunityParameters();
   
       void writeSpeciationRates();
   
       void calculateTree();
   
       void makeSpeciationRatesUnique();
   
       void makeTimesUnique();
   
       void output();
   
       void printEndTimes(time_t tStart, time_t tEnd);
   
       void apply(shared_ptr<SpecSimParameters> sp);
   
       virtual void applyNoOutput(shared_ptr<SpecSimParameters> sp);
   
       void doApplication(shared_ptr<SpecSimParameters> sp);
   
       void doApplication(shared_ptr<SpecSimParameters> sp, shared_ptr<vector<TreeNode>> data);
   
       void doApplicationInternal(shared_ptr<SpecSimParameters> sp, shared_ptr<vector<TreeNode>> data);
   
       void speciateRemainingLineages(const string &filename);
   
       unsigned long getSpeciesRichness(const unsigned long &community_reference);
   
       shared_ptr<map<unsigned long, unsigned long>> getSpeciesAbundances(const unsigned long &community_reference);
   
       shared_ptr<vector<unsigned long>> getSpeciesAbundances();
   };
   
   #endif

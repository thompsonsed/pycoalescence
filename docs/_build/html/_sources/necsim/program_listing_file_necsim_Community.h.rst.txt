
.. _program_listing_file_necsim_Community.h:

Program Listing for File Community.h
====================================

- Return to documentation for :ref:`file_necsim_Community.h`

.. code-block:: cpp

   //This file is part of NECSim project which is released under MIT license.
   //See file **LICENSE.txt** or visit https://opensource.org/licenses/MIT) for full license details.
   #ifndef TREELIST
   #define TREELIST
   
   #include <cmath>
   #include <sqlite3.h>
   #include <cstring>
   #include <cmath>
   #include <stdexcept>
   #include <string>
   # include <boost/filesystem.hpp>
   #include <boost/lexical_cast.hpp>
   #include <set>
   
   #include "TreeNode.h"
   #include "Matrix.h"
   #include "DataMask.h"
   #include "SpecSimParameters.h"
   
   using namespace std;
   using std::string;
   
   bool checkSpeciation(const long double &random_number, const long double &speciation_rate,
                        const unsigned long &no_generations);
   
   struct CommunityParameters
   {
       unsigned long reference;
       long double speciation_rate;
       long double time;
       bool fragment;
       unsigned long metacommunity_reference; // will be 0 if no metacommunity used.
       // protracted speciation parameters
       ProtractedSpeciationParameters protracted_parameters;
       bool updated; // set to true if the fragment reference needs updating in the database
   
       CommunityParameters() : reference(0), speciation_rate(0.0), time(0), fragment(false), metacommunity_reference(0),
                               protracted_parameters(), updated(false){}
   
       CommunityParameters(unsigned long reference_in, long double speciation_rate_in, long double time_in,
                           bool fragment_in, unsigned long metacommunity_reference_in,
                           const ProtractedSpeciationParameters &protracted_params);
   
       void setup(unsigned long reference_in, long double speciation_rate_in, long double time_in, bool fragment_in,
                  unsigned long metacommunity_reference_in, const ProtractedSpeciationParameters &protracted_params);
   
       bool compare(long double speciation_rate_in, long double time_in, bool fragment_in,
                    unsigned long metacommunity_reference_in,
                    const ProtractedSpeciationParameters &protracted_params);
   
       bool compare(long double speciation_rate_in, long double time_in,
                    unsigned long metacommunity_reference_in,
                    const ProtractedSpeciationParameters &protracted_params);
   
       bool compare(unsigned long reference_in);
   };
   
   struct CommunitiesArray
   {
       vector<CommunityParameters> communityParameters;
   
       void pushBack(unsigned long reference, long double speciation_rate, long double time, bool fragment,
                     unsigned long metacommunity_reference,
                     const ProtractedSpeciationParameters &protracted_params);
   
       void pushBack(CommunityParameters tmp_param);
   
       CommunityParameters &addNew(long double speciation_rate, long double time, bool fragment,
                                   unsigned long metacommunity_reference,
                                   const ProtractedSpeciationParameters &protracted_params);
   
       bool hasPair(long double speciation_rate, double time, bool fragment,
                    unsigned long metacommunity_reference,
                    const ProtractedSpeciationParameters &protracted_params);
   
   };
   
   struct MetacommunityParameters
   {
       unsigned long reference;
       unsigned long metacommunity_size;
       long double speciation_rate;
   
       MetacommunityParameters(unsigned long reference_in, long double speciation_rate_in,
                               unsigned long metacommunity_size_in);
   
       bool compare(long double speciation_rate_in, unsigned long metacommunity_size_in);
   
       bool compare(unsigned long reference_in);
   };
   
   struct MetacommunitiesArray
   {
       vector<MetacommunityParameters> calc_array;
   
       void pushBack(unsigned long reference, long double speciation_rate, unsigned long metacommunity_size);
   
       void pushBack(MetacommunityParameters tmp_param);
   
       unsigned long addNew(long double speciation_rate, unsigned long metacommunity_size);
   
       bool hasPair(long double speciation_rate, unsigned long metacommunity_size);
   
       bool hasPair(unsigned long reference);
   
       unsigned long getReference(long double speciation_rate, unsigned long metacommunity_size);
   };
   
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
       sqlite3 *outdatabase; // stores the file database connection
       bool bSqlConnection; // true if the data connection has been established.
       Row<TreeNode> *nodes; // in older versions this was called list. Changed to avoid confusion with the built-in class.
       Row<unsigned long> row_out;
       unsigned long iSpecies;
       bool has_imported_samplemask; // checks whether the samplemask has already been imported.
       bool has_imported_data; // checks whether the main sim data has been imported.
       Samplematrix samplemask; // the samplemask object for defining the areas we want to sample from.
       vector<Fragment> fragments; // a vector of fragments for storing each fragment's coordinates.
       CommunityParameters *current_community_parameters;
       // the minimum speciation rate the original simulation was run with (this is read from the database SIMULATION_PARAMETERS table)
       long double min_spec_rate;
       // The dimensions of the sample grid size.
       unsigned long grid_x_size, grid_y_size;
       // The dimensions of the original sample map file
       unsigned long samplemask_x_size, samplemask_y_size, samplemask_x_offset, samplemask_y_offset;
       // Vector containing past speciation rates
       CommunitiesArray past_communities;
       MetacommunitiesArray past_metacommunities;
       // Protracted speciation parameters
       bool protracted;
       double min_speciation_gen, max_speciation_gen;
       ProtractedSpeciationParameters applied_protracted_parameters;
       unsigned long max_species_id, max_fragment_id, max_locations_id;
       // Does not need to be stored during simulation pause
       SpecSimParameters *spec_sim_parameters;
   public:
   
       Community(Row<TreeNode> *r) : nodes(r), applied_protracted_parameters()
       {
           in_mem = false;
           iSpecies = 0;
           has_imported_samplemask = false;
           bSqlConnection = false;
           database_set = false;
           has_imported_data = false;
           min_speciation_gen = 0.0;
           max_speciation_gen = 0.0;
           protracted = false;
           current_community_parameters = nullptr;
           max_species_id = 0;
           max_locations_id = 0;
   
       }
   
       Community() : applied_protracted_parameters()
       {
           in_mem = false;
           iSpecies = 0;
           has_imported_samplemask = false;
           bSqlConnection = false;
           database_set = false;
           has_imported_data = false;
           min_speciation_gen = 0.0;
           max_speciation_gen = 0.0;
           protracted = false;
           current_community_parameters = nullptr;
           max_species_id = 0;
           max_locations_id = 0;
       }
   
        virtual ~Community()
       {
           nodes = nullptr;
       }
   
       void setList(Row<TreeNode> *l);
   
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
   
       void setInternalDatabase();
   
       void internalOption();
   
       void importData(string inputfile);
   
       void setSimParameters(const SimParameters *sim_parameters);
   
       void importSimParameters(string file);
   
       bool isSetDatabase();
   
       void getMaxSpeciesAbundancesID();
   
       Row<unsigned long> *getCumulativeAbundances();
   
       Row<unsigned long> getRowOut();
   
       unsigned long getSpeciesNumber();
   
       void getMaxFragmentAbundancesID();
   
       void getMaxSpeciesLocationsID();
   
       void setProtractedParameters(const ProtractedSpeciationParameters &protracted_params);
   
       void overrideProtractedParameters(const ProtractedSpeciationParameters &protracted_params);
   
       void setProtracted(bool protracted_in);
   
       void createDatabase();
   
       void generateCoalescenceTree();
   
       void outputSpeciesAbundances();
   
       bool checkCalculationsPerformed(long double speciation_rate, double time, bool fragments,
                                       unsigned long metacommunity_size, long double metacommunity_speciation_rate,
                                       ProtractedSpeciationParameters proc_parameters);
   
       void addCalculationPerformed(long double speciation_rate, double time, bool fragments,
                                    unsigned long metacommunity_size, long double metacommunity_speciation_rate,
                                    const ProtractedSpeciationParameters &protracted_params);
   
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
   
       void writeNewMetacommuntyParameters();
   
       void updateCommunityParameters();
   
       void writeSpeciationRates();
   
       void calculateTree();
   
       void output();
   
       void printEndTimes(time_t tStart, time_t tEnd);
   
       void apply(SpecSimParameters *sp);
   
       virtual void applyNoOutput(SpecSimParameters *sp);
   
       void doApplication(SpecSimParameters *sp);
   
       void doApplication(SpecSimParameters *sp, Row<TreeNode> *data);
   
       void doApplicationInternal(SpecSimParameters *sp, Row<TreeNode> *data);
   
   };
   
   #endif

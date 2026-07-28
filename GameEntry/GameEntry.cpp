#include <iostream>
#include <string>
using namespace std;
class GameEntry {
    public:
        GameEntry(const string& n="", int s=0); // constructor
        string getName() const; // get player name
        int getScore() const; // get score
    private:
        string name;
        int score;
};
// stores game high scores
class Scores{
    public:  
        Scores(int maxEnt=10); // constructor
        ~Scores();  // destructor
        void add(const GameEntry& e); // add a game entry  GameEntry
        GameEntry remove(int i); // remove the ith entry
        // throw(IndexOutOfBounds);
        void print() const; // print the entries
    private:
        int maxEntries; // maximum number of entries
        int numEntries; // actual number of entries
        GameEntry* entries; // array of game entries
};
Scores::Scores(int maxEnt) {  
    maxEntries = maxEnt;  
    entries = new GameEntry[maxEntries];  
    numEntries = 0;
}
Scores::~Scores(){  
    delete[] entries;
}
GameEntry::GameEntry(const string& n, int s) {
    name = n;
    score = s;
}
string GameEntry::getName() const {
    return name;
}
int GameEntry::getScore() const {
    return score;
}
void Scores::add(const GameEntry& e) {
    bool isDuplicate = false;
    
    // check if there is same name in the entries
    for (int i=0; i<numEntries;i++){
        if (entries[i].getName()==e.getName()){
            isDuplicate = true;
            if (entries[i].getScore()<e.getScore()){
                entries[i] = e;
            }
            break;
        }
    }

    // check if there is space in the entries
    if (!isDuplicate){
        if (numEntries < maxEntries){
            entries[numEntries] = e;
            numEntries++;
        }
        else if (e.getScore() > entries[numEntries-1].getScore()){
            entries[numEntries-1] = e;
        }
    }

    // sort the entries in descending order
    for (int i=0; i<numEntries-1;i++){
        for (int j=i+1;j<numEntries;j++){
            if (entries[i].getScore()<entries[j].getScore()){
                GameEntry temp = entries[i];
                entries[i] = entries[j];
                entries[j] = temp;
            }
        }
    }
}
GameEntry Scores::remove(int i) {
    if (i<0 || i>=numEntries){
        printf("Invalid number\n");
        return GameEntry(); // Return a default GameEntry
    }
    GameEntry temp = entries[i];
    for (int j=i;j<numEntries-1;j++){
        entries[j] = entries[j+1];
    }
    numEntries--;
    return temp;
}
void Scores::print() const{
    for (int i=0; i<numEntries; i++){
        printf("Rank %d: %s %d\n", i+1, entries[i].getName().c_str(), entries[i].getScore());
    }
}
int main() {
    Scores scores(10);

    int ScoreInput;
    string NameInput;

    while(1){
        printf("1 : Add Entry\n");
        printf("2 : Print Entries\n");
        printf("3 : Remove Entry\n");
        printf("4 : Exit\n");
        printf("Select Menu : ");

        int Input;
        cin >> Input;

        switch(Input){
            case 1:{
                printf("Enter Name and Score : ");
                cin >> NameInput >> ScoreInput;
                GameEntry entry(NameInput, ScoreInput);
                scores.add(entry);
                break;
            }
            case 2:{
                printf("Rank\tName\tScore\n");
                scores.print();
                break;
            }
            case 3:{
                printf("Enter Rank to Remove : ");
                int removeRank;
                cin >> removeRank;
                scores.remove(removeRank-1);
                break;
            }
            case 4:
                printf("Exit\n");
                return 0;
            default:
                cout << "Invalid input" << endl;
                continue;
        }
    }
    return 0;
}

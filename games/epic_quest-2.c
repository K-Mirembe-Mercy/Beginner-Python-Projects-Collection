#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define RST  "\033[0m"
#define BLD  "\033[1m"
#define RED  "\033[1;31m"
#define GRN  "\033[1;32m"
#define YLW  "\033[1;33m"
#define BLU  "\033[1;34m"
#define MAG  "\033[1;35m"
#define CYN  "\033[1;36m"
#define WHT  "\033[1;37m"
#define DRED "\033[0;31m"
#define DGRN "\033[0;32m"
#define DYLW "\033[0;33m"
#define DCYN "\033[0;36m"

#define MAX_NAME   32
#define MAX_INV    20
#define MAX_QUESTS 10
#define SAVE_FILE  "epicquest.sav"

#define IT_WEAPON 0
#define IT_ARMOR  1
#define IT_POTION 2
#define IT_ELIXIR 3
#define IT_RUNE   4
#define IT_KEY    5

#define CL_WARRIOR 0
#define CL_MAGE    1
#define CL_ROGUE   2
#define CL_PALADIN 3

typedef struct { char name[32]; int type,value,power,qty; } Item;
typedef struct { char desc[64]; int target_kills,kills,reward_gold,reward_exp,done,claimed; } Quest;

typedef struct {
    char  name[MAX_NAME];
    int   class_type,level,exp,exp_next;
    int   hp,max_hp,mp,max_mp;
    int   atk,def,speed;
    int   gold,gems;
    int   kills,total_kills,deaths;
    int   arena_wins,arena_losses;
    int   streak,prestige;
    long  total_gold_earned;
    int   world_level;
    Item  inv[MAX_INV];
    int   inv_size;
    Quest quests[MAX_QUESTS];
    int   quest_count;
    int   weapon_eq,armor_eq,rune_eq;
} Player;

typedef struct {
    char name[32];
    int  hp,max_hp,atk,def;
    int  exp_reward,gold_min,gold_max;
    int  level_req,world;
    char sym[4];
} Enemy;

Player P;
int running=1;

Enemy ENEMIES[50]={
    {"Slime",          15, 15,  3,  1,   8,  2,  6,  1,1,"(G)"},
    {"Goblin",         25, 25,  5,  2,  12,  4, 10,  1,1,"(B)"},
    {"Wolf",           35, 35,  7,  3,  18,  6, 14,  2,1,"(W)"},
    {"Bandit",         45, 45,  9,  4,  24,  8, 18,  3,1,"(X)"},
    {"Forest Troll",   70, 70, 13,  6,  38, 12, 24,  4,1,"(T)"},
    {"Bat Swarm",      40, 40,  8,  2,  22,  8, 16,  5,2,"(b)"},
    {"Cave Spider",    55, 55, 11,  4,  30, 10, 20,  5,2,"(S)"},
    {"Rock Golem",     90, 90, 14,  9,  44, 14, 28,  6,2,"(R)"},
    {"Dark Dwarf",     65, 65, 13,  6,  36, 12, 22,  7,2,"(D)"},
    {"Cave Drake",    110,110, 18, 10,  58, 18, 34,  8,2,"(~)"},
    {"Swamp Hag",      75, 75, 15,  5,  42, 14, 26,  9,3,"(H)"},
    {"Poison Frog",    60, 60, 12,  3,  34, 10, 20,  9,3,"(F)"},
    {"Bog Monster",   130,130, 22, 12,  66, 22, 40, 10,3,"(M)"},
    {"Cursed Knight", 100,100, 20, 14,  58, 20, 36, 11,3,"(K)"},
    {"Witch Doctor",  115,115, 24,  8,  70, 24, 44, 12,3,"(!)"},
    {"Fire Imp",       90, 90, 20,  6,  54, 18, 32, 13,4,"(i)"},
    {"Lava Crab",     140,140, 24, 16,  72, 26, 46, 14,4,"(C)"},
    {"Magma Brute",   170,170, 28, 18,  88, 30, 54, 15,4,"(V)"},
    {"Flame Wraith",  125,125, 30, 10,  80, 28, 50, 16,4,"(w)"},
    {"Inferno Drake", 220,220, 35, 20, 110, 40, 70, 17,4,"(d)"},
    {"Ghost",         110,110, 26,  4,  70, 24, 42, 18,5,"(g)"},
    {"Skeleton Archer",130,130,30,  8,  80, 28, 50, 19,5,"(s)"},
    {"Lich",          180,180, 36, 14,  96, 34, 60, 20,5,"(L)"},
    {"Vampire",       200,200, 38, 18, 108, 38, 66, 21,5,"(v)"},
    {"Haunted Armor", 250,250, 42, 28, 130, 46, 80, 22,5,"(A)"},
    {"Sea Serpent",   200,200, 38, 16, 108, 38, 66, 23,6,"(~)"},
    {"Kraken Arm",    260,260, 44, 20, 136, 48, 84, 24,6,"(O)"},
    {"Deep Horror",   300,300, 50, 24, 158, 56, 98, 25,6,"(*)"},
    {"Abyssal Shark", 280,280, 48, 22, 148, 52, 90, 26,6,"(^)"},
    {"Leviathan",     400,400, 58, 30, 200, 70,120, 27,6,"(Z)"},
    {"Ice Wraith",    240,240, 46, 20, 130, 46, 80, 28,7,"(*)"},
    {"Frost Giant",   380,380, 60, 34, 190, 68,116, 29,7,"(G)"},
    {"Blizzard Wolf", 310,310, 54, 28, 165, 58,100, 30,7,"(W)"},
    {"Glacier Golem", 450,450, 64, 40, 220, 78,134, 31,7,"(#)"},
    {"Yeti King",     520,520, 70, 42, 260, 92,158, 32,7,"(Y)"},
    {"Shadow Fiend",  350,350, 66, 28, 190, 68,116, 33,8,"(f)"},
    {"Nightmare",     420,420, 74, 32, 226, 80,138, 34,8,"(N)"},
    {"Void Walker",   500,500, 80, 36, 266, 94,162, 35,8,"(V)"},
    {"Dark Titan",    600,600, 88, 44, 314,112,192, 36,8,"(T)"},
    {"Chaos Lord",    700,700, 96, 50, 365,130,224, 37,8,"(!)"},
    {"Wyvern",        500,500, 88, 36, 270, 96,165, 38,9,"(~)"},
    {"Dragon Guard",  600,600, 96, 44, 318,112,194, 39,9,"(X)"},
    {"Elder Drake",   750,750,108, 52, 396,140,242, 40,9,"(D)"},
    {"Ancient Dragon",900,900,120, 60, 474,168,290, 41,9,"(R)"},
    {"Dragon Emperor",1100,1100,136,70,576,204,352, 43,9,"(E)"},
    {"Void Sentinel", 800,800,120, 58, 440,156,270, 44,10,"(V)"},
    {"Oblivion Mage", 900,900,132, 60, 500,178,306, 45,10,"(M)"},
    {"Eternal Knight",1100,1100,148,74,590,210,362, 46,10,"(K)"},
    {"The Corrupted",1300,1300,164,82,690,246,424,  48,10,"(C)"},
    {"OMEGA-FINAL",  2000,2000,200,100,1000,500,1000,50,10,"(O)"},
};

Item SHOP[22]={
    {"Minor Potion",IT_POTION,25,40,1},{"Health Potion",IT_POTION,60,80,1},
    {"Major Potion",IT_POTION,130,150,1},{"Full Restore",IT_POTION,300,999,1},
    {"Mana Potion",IT_ELIXIR,50,50,1},{"Power Elixir",IT_ELIXIR,200,120,1},
    {"Iron Sword",IT_WEAPON,80,8,1},{"Steel Blade",IT_WEAPON,200,16,1},
    {"Enchanted Axe",IT_WEAPON,450,28,1},{"Shadow Dagger",IT_WEAPON,800,40,1},
    {"Dragonbone Sword",IT_WEAPON,1800,65,1},{"Void Slicer",IT_WEAPON,4000,100,1},
    {"Leather Armor",IT_ARMOR,90,6,1},{"Chain Mail",IT_ARMOR,220,14,1},
    {"Plate Armor",IT_ARMOR,500,24,1},{"Dragon Scale",IT_ARMOR,1200,40,1},
    {"Shadow Cloak",IT_ARMOR,2500,60,1},{"Void Mantle",IT_ARMOR,5000,90,1},
    {"Speed Rune",IT_RUNE,300,10,1},{"Fury Rune",IT_RUNE,500,18,1},
    {"Titan Rune",IT_RUNE,1000,30,1},{"Omega Rune",IT_RUNE,3000,55,1},
};

Item GEMS[5]={
    {"XP Boost (2x)",IT_ELIXIR,5,200,1},
    {"Gold Magnet",IT_ELIXIR,8,500,1},
    {"Auto-Revive Charm",IT_ELIXIR,10,1,1},
    {"Legendary Chest",IT_WEAPON,20,120,1},
    {"Prestige Token",IT_KEY,50,1,1},
};

void cls(void){printf("\033[2J\033[H");fflush(stdout);}
void pause_p(void){printf("\n"YLW"  [ ENTER to continue ]"RST);getchar();}
int rng(int lo,int hi){return lo+rand()%(hi-lo+1);}

void bar(const char*col,const char*sym,int cur,int max,int w){
    int f=(max>0)?(cur*w/max):0;if(f>w)f=w;
    printf("%s[",col);
    for(int i=0;i<w;i++)printf("%s",i<f?sym:" ");
    printf("%s]"RST,col);
}

void banner(void){
    printf(RED BLD
    "\n"
    " ███████╗██████╗ ██╗ ██████╗    ██████╗ ██╗   ██╗███████╗███████╗████████╗\n"
    " ██╔════╝██╔══██╗██║██╔════╝   ██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝\n"
    " █████╗  ██████╔╝██║██║        ██║   ██║██║   ██║█████╗  ███████╗   ██║   \n"
    " ██╔══╝  ██╔═══╝ ██║██║        ██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║   \n"
    " ███████╗██║     ██║╚██████╗   ╚██████╔╝╚██████╔╝███████╗███████║   ██║   \n"
    " ╚══════╝╚═╝     ╚═╝ ╚═════╝    ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝   \n"
    RST);
    printf(YLW"  50 Levels | 10 Worlds | Arena | Shop | Quests | Prestige\n\n"RST);
}

void apply_class(void){
    switch(P.class_type){
        case CL_WARRIOR:P.max_hp+=30;P.atk+=4;P.def+=4;P.max_mp=30;break;
        case CL_MAGE:   P.max_hp+=10;P.atk+=8;P.max_mp=80;P.speed+=2;break;
        case CL_ROGUE:  P.atk+=6;P.speed+=5;P.max_mp=40;P.max_hp+=15;break;
        case CL_PALADIN:P.max_hp+=40;P.def+=8;P.max_mp=60;P.atk+=2;break;
    }
    P.hp=P.max_hp;P.mp=P.max_mp;
}

void hud(void){
    const char*cls[]={"Warrior","Mage","Rogue","Paladin"};
    const char*wn[]={"","Greenwood Forest","Dark Caverns","Cursed Swamp","Volcanic Wastes",
        "Haunted Ruins","Ocean Depths","Frozen Tundra","Shadow Realm","Dragon's Peak","The Void"};
    int w=P.world_level<1?1:(P.world_level>10?10:P.world_level);
    printf(CYN"\n  ╔══════════════════════════════════════════════════════╗\n"RST);
    printf(CYN"  ║ "RST BLD"%-14s"RST" [%s] Lv."YLW"%-3d"RST" World:"MAG" %-18s"RST CYN"║\n"RST,
        P.name,cls[P.class_type],P.level,wn[w]);
    printf(CYN"  ╠══════════════════════════════════════════════════════╣\n"RST);
    printf(CYN"  ║"RST"  HP  ");bar(RED,"#",P.hp,P.max_hp,20);printf(RED" %4d/%-4d"RST CYN"║\n"RST,P.hp,P.max_hp);
    printf(CYN"  ║"RST"  MP  ");bar(BLU,"=",P.mp,P.max_mp,20);printf(BLU" %4d/%-4d"RST CYN"║\n"RST,P.mp,P.max_mp);
    printf(CYN"  ║"RST"  EXP ");bar(DGRN,"-",P.exp,P.exp_next,20);printf(GRN" %4d/%-4d"RST CYN"║\n"RST,P.exp,P.exp_next);
    printf(CYN"  ╠══════════════════════════════════════════════════════╣\n"RST);
    printf(CYN"  ║"RST" ATK:"YLW"%-5d"RST" DEF:"YLW"%-5d"RST" SPD:"YLW"%-4d"RST" Gold:"YLW"%-8d"RST" Gems:"MAG"%-4d"RST CYN"║\n"RST,
        P.atk,P.def,P.speed,P.gold,P.gems);
    printf(CYN"  ║"RST" Kills:"GRN"%-7d"RST" Deaths:"RED"%-4d"RST" Arena:"YLW"%dW-%dL"RST" Streak:"GRN"%-3d"RST"      "CYN"║\n"RST,
        P.total_kills,P.deaths,P.arena_wins,P.arena_losses,P.streak);
    printf(CYN"  ╚══════════════════════════════════════════════════════╝\n\n"RST);
}

void lvlup(void){
    P.level++;P.exp-=P.exp_next;
    P.exp_next=(int)(P.exp_next*1.35+50);
    int hg=rng(8,15)+(P.class_type==CL_WARRIOR?5:P.class_type==CL_PALADIN?6:2);
    int ag=rng(1,3)+(P.class_type==CL_MAGE?2:P.class_type==CL_ROGUE?2:1);
    int dg=rng(1,2)+(P.class_type==CL_PALADIN?2:P.class_type==CL_WARRIOR?1:0);
    P.max_hp+=hg;P.hp=P.max_hp;P.atk+=ag;P.def+=dg;
    P.max_mp+=rng(2,6)+(P.class_type==CL_MAGE?6:2);P.mp=P.max_mp;
    if(P.class_type==CL_ROGUE)P.speed++;
    if(P.level%5==0&&P.world_level<10)P.world_level++;
    printf(YLW"\n  ╔══════════════════════════════╗\n");
    printf("  ║   *** LEVEL UP! Level %-3d ***  ║\n",P.level);
    printf("  ║  +%2d HP  +%d ATK  +%d DEF       ║\n",hg,ag,dg);
    if(P.level%5==0)printf(MAG"  ║  >>> NEW WORLD UNLOCKED! <<<  ║\n"YLW);
    if(P.level==50) printf(RED"  ║  *** MAX LEVEL REACHED! ***   ║\n"YLW);
    printf("  ╚══════════════════════════════╝\n"RST);
}

void gain_exp(int n){
    P.exp+=n;
    while(P.exp>=P.exp_next&&P.level<50)lvlup();
    if(P.level>=50)P.exp=P.exp_next;
}

void save_g(void){
    FILE*f=fopen(SAVE_FILE,"wb");
    if(!f){printf(RED"  Save failed!\n"RST);return;}
    fwrite(&P,sizeof(Player),1,f);fclose(f);
    printf(GRN"  Game saved!\n"RST);
}

int load_g(void){
    FILE*f=fopen(SAVE_FILE,"rb");
    if(!f)return 0;
    fread(&P,sizeof(Player),1,f);fclose(f);return 1;
}

void new_game(void){
    cls();banner();
    printf(WHT"  Enter hero name: "RST);
    scanf(" %31s",P.name);while(getchar()!='\n');
    printf(CYN"\n  Choose class:\n\n"RST);
    printf(YLW"  [1]"RST" WARRIOR  — High HP/DEF, strong and tough\n");
    printf(YLW"  [2]"RST" MAGE     — Massive ATK and MP, glass cannon\n");
    printf(YLW"  [3]"RST" ROGUE    — Speed and crits, deadly striker\n");
    printf(YLW"  [4]"RST" PALADIN  — Tank+healer, almost unkillable\n\n");
    printf(WHT"  > "RST);
    int c;scanf("%d",&c);while(getchar()!='\n');
    if(c<1||c>4)c=1;
    memset(&P,0,sizeof(Player));
    P.class_type=c-1;P.level=1;P.exp=0;P.exp_next=100;
    P.max_hp=80;P.hp=80;P.max_mp=40;P.mp=40;
    P.atk=10;P.def=5;P.speed=5;
    P.gold=50;P.gems=10;P.world_level=1;P.streak=1;
    P.weapon_eq=-1;P.armor_eq=-1;P.rune_eq=-1;
    apply_class();
    P.quest_count=3;
    strcpy(P.quests[0].desc,"Slay 5 monsters");
    P.quests[0].target_kills=5;P.quests[0].reward_gold=100;P.quests[0].reward_exp=80;
    strcpy(P.quests[1].desc,"Slay 15 monsters");
    P.quests[1].target_kills=15;P.quests[1].reward_gold=300;P.quests[1].reward_exp=250;
    strcpy(P.quests[2].desc,"Slay 30 monsters");
    P.quests[2].target_kills=30;P.quests[2].reward_gold=700;P.quests[2].reward_exp=600;
    const char*cn[]={"Warrior","Mage","Rogue","Paladin"};
    printf(GRN"\n  Welcome, %s the %s! Adventure begins!\n"RST,P.name,cn[P.class_type]);
    pause_p();
}

void use_potion_in_battle(void){
    for(int i=0;i<P.inv_size;i++){
        if(P.inv[i].type==IT_POTION&&P.inv[i].qty>0){
            P.hp+=P.inv[i].power;if(P.hp>P.max_hp)P.hp=P.max_hp;
            printf(GRN"  Used %s! Healed %d HP!\n"RST,P.inv[i].name,P.inv[i].power);
            P.inv[i].qty--;
            if(P.inv[i].qty==0){for(int j=i;j<P.inv_size-1;j++)P.inv[j]=P.inv[j+1];P.inv_size--;}
            return;
        }
    }
    printf(RED"  No potions!\n"RST);
}

void combat(int ei){
    Enemy E=ENEMIES[ei];int e_hp=E.hp;
    cls();
    printf(RED BLD"\n  *** BATTLE: %s %s ***\n"RST,E.sym,E.name);
    printf(DCYN"  Enemy HP:%d ATK:%d DEF:%d\n\n"RST,E.hp,E.atk,E.def);
    int acted=1;
    while(P.hp>0&&e_hp>0){
        printf(CYN"  ─────────────────────────────────\n"RST);
        printf("  YOUR HP:");bar(RED,"#",P.hp,P.max_hp,16);printf(RED" %d/%d\n"RST,P.hp,P.max_hp);
        printf("  ENEMY HP:");bar(DRED,"#",e_hp,E.max_hp,16);printf(RED" %d/%d\n\n"RST,e_hp>0?e_hp:0,E.max_hp);
        printf(YLW"[1]"RST"Attack  "YLW"[2]"RST"Power(-10MP)  "YLW"[3]"RST"Potion  "YLW"[4]"RST"Flee\n");
        printf(WHT"> "RST);
        int a;scanf("%d",&a);while(getchar()!='\n');
        acted=1;
        if(a==1){
            int d=rng(P.atk-3,P.atk+5)-rng(0,E.def/2);if(d<1)d=1;
            if(rng(1,100)<=(P.class_type==CL_ROGUE?25:10)){d=(int)(d*1.8);printf(YLW"  CRITICAL HIT!\n"RST);}
            e_hp-=d;printf(GRN"  You deal %d damage!\n"RST,d);
        }else if(a==2){
            if(P.mp>=10){P.mp-=10;
                int d=rng(P.atk+5,P.atk+15)-rng(0,E.def/3);if(d<2)d=2;
                if(rng(1,100)<=(P.class_type==CL_MAGE?30:15)){d=(int)(d*2.0);printf(YLW"  MEGA CRIT!\n"RST);}
                if(P.class_type==CL_MAGE)d=(int)(d*1.25);
                e_hp-=d;printf(MAG"  Power Strike: %d damage!\n"RST,d);
            }else printf(RED"  Not enough MP!\n"RST);
        }else if(a==3){use_potion_in_battle();
        }else if(a==4){
            int fc=40+P.speed*2+(P.class_type==CL_ROGUE?25:0);if(fc>90)fc=90;
            if(rng(1,100)<=fc){printf(YLW"  You fled!\n"RST);pause_p();return;}
            else printf(RED"  Couldn't escape!\n"RST);
        }else{printf(RED"  Invalid!\n"RST);acted=0;}
        if(!acted)continue;
        if(e_hp>0){
            int ed=rng(E.atk-3,E.atk+4)-rng(0,P.def/2);if(ed<1)ed=1;
            if(P.class_type==CL_PALADIN)ed=(int)(ed*0.85);
            P.hp-=ed;printf(RED"  %s attacks! -%d HP!\n"RST,E.name,ed);
        }
        usleep(200000);
    }
    if(P.hp<=0){
        P.hp=1;P.deaths++;int lost=P.gold/5;P.gold-=lost;
        printf(RED BLD"\n  *** YOU DIED! Lost %d gold ***\n"RST,lost);
        printf(DCYN"  Respawning with 1 HP...\n"RST);pause_p();return;
    }
    int ge=rng(E.gold_min,E.gold_max)+(P.class_type==CL_ROGUE?rng(2,6):0);
    P.gold+=ge;P.total_gold_earned+=ge;P.kills++;P.total_kills++;
    for(int i=0;i<P.quest_count;i++){
        if(!P.quests[i].done){P.quests[i].kills++;
            if(P.quests[i].kills>=P.quests[i].target_kills)P.quests[i].done=1;}
    }
    printf(GRN BLD"\n  *** VICTORY! %s defeated! ***\n"RST,E.name);
    printf(YLW"  +%d gold  +%d EXP\n"RST,ge,E.exp_reward);
    if(rng(1,100)<=20&&P.inv_size<MAX_INV){
        int di=rng(0,21);P.inv[P.inv_size++]=SHOP[di];
        printf(MAG"  ITEM DROP: %s!\n"RST,SHOP[di].name);}
    if(rng(1,100)<=5){int gm=rng(1,3);P.gems+=gm;printf(MAG"  Gem drop: +%d gems!\n"RST,gm);}
    gain_exp(E.exp_reward);pause_p();
}

void go_hunt(void){
    cls();int w=P.world_level;
    printf(MAG BLD"\n  *** HUNT — World %d ***\n\n"RST,w);
    int shown[50];int sc=0;
    for(int i=0;i<50;i++){
        if(ENEMIES[i].world>=w&&ENEMIES[i].world<=w+1&&P.level>=ENEMIES[i].level_req-3){
            shown[sc++]=i;
            int delta=ENEMIES[i].level_req-P.level;
            const char*diff;
            if(delta<=-3)diff=GRN"Easy  "RST;
            else if(delta<=0)diff=DYLW"Normal"RST;
            else if(delta<=3)diff=DRED"Hard  "RST;
            else diff=RED"DANGER"RST;
            printf("  "YLW"[%d]"RST" %s %-22s HP:%-5d ATK:%-4d %s\n",
                sc,ENEMIES[i].sym,ENEMIES[i].name,ENEMIES[i].hp,ENEMIES[i].atk,diff);
            if(sc>=8)break;
        }
    }
    if(sc==0){printf(RED"  No enemies available here.\n"RST);pause_p();return;}
    printf(YLW"\n  [0]"RST" Back\n"WHT"  Choose: "RST);
    int c;scanf("%d",&c);while(getchar()!='\n');
    if(c>=1&&c<=sc)combat(shown[c-1]);
}

void shop_menu(void){
    int done=0;
    while(!done){
        cls();
        printf(YLW BLD"\n  *** SHOP ***\n\n"RST);
        printf(CYN"  Gold: "YLW"%d"RST"  Gems: "MAG"%d\n\n"RST,P.gold,P.gems);
        printf(BLD"  -- GOLD SHOP --\n"RST);
        const char*ts[]={"Weapon","Armor ","Potion","Elixir","Rune  ","Key   "};
        for(int i=0;i<22;i++){
            char ok=P.gold>=SHOP[i].value?' ':'x';
            printf("  "YLW"[%2d]"RST" %s %-22s "CYN"%5dg"RST" pwr:+%d %c\n",
                i+1,ts[SHOP[i].type],SHOP[i].name,SHOP[i].value,SHOP[i].power,ok);
        }
        printf(BLD"\n  -- GEM SHOP (Premium) --\n"RST);
        for(int i=0;i<5;i++){
            char ok=P.gems>=GEMS[i].value?' ':'x';
            printf("  "MAG"[G%d]"RST" %-26s "MAG"%2d gems"RST" %c\n",i+1,GEMS[i].name,GEMS[i].value,ok);
        }
        printf(YLW"\n  [0]"RST" Back  "YLW"[S]"RST" Sell\n"WHT"  > "RST);
        char inp[16];scanf(" %15s",inp);while(getchar()!='\n');
        if(inp[0]=='0')done=1;
        else if(inp[0]=='S'||inp[0]=='s'){
            if(P.inv_size==0){printf(RED"  Empty!\n"RST);pause_p();continue;}
            for(int i=0;i<P.inv_size;i++)
                printf("  "YLW"[%d]"RST" %-22s sell:%dg\n",i+1,P.inv[i].name,P.inv[i].value/2);
            printf(WHT"  Sell (0=back): "RST);int s;scanf("%d",&s);while(getchar()!='\n');
            if(s>=1&&s<=P.inv_size){
                int gn=P.inv[s-1].value/2;P.gold+=gn;
                printf(GRN"  Sold %s for %dg!\n"RST,P.inv[s-1].name,gn);
                for(int j=s-1;j<P.inv_size-1;j++)P.inv[j]=P.inv[j+1];P.inv_size--;
                pause_p();}
        }else if(inp[0]=='G'||inp[0]=='g'){
            int gi=atoi(inp+1)-1;
            if(gi>=0&&gi<5){
                if(P.gems<GEMS[gi].value){printf(RED"  Not enough gems!\n"RST);}
                else if(P.inv_size>=MAX_INV){printf(RED"  Inventory full!\n"RST);}
                else{P.gems-=GEMS[gi].value;P.inv[P.inv_size++]=GEMS[gi];
                    printf(GRN"  Got %s!\n"RST,GEMS[gi].name);
                    if(gi==3){int pw=rng(80,130);snprintf(P.inv[P.inv_size-1].name,32,"Leg.Blade+%d",pw);
                        P.inv[P.inv_size-1].power=pw;P.inv[P.inv_size-1].type=IT_WEAPON;
                        printf(YLW"  Legendary Blade+%d!\n"RST,pw);}
                }
                pause_p();}
        }else{
            int bi=atoi(inp)-1;
            if(bi>=0&&bi<22){
                if(P.gold<SHOP[bi].value){printf(RED"  Not enough gold!\n"RST);}
                else if(P.inv_size>=MAX_INV){printf(RED"  Inventory full!\n"RST);}
                else{P.gold-=SHOP[bi].value;P.inv[P.inv_size++]=SHOP[bi];
                    printf(GRN"  Got %s!\n"RST,SHOP[bi].name);}
                pause_p();}
        }
    }
}

void inv_menu(void){
    cls();printf(CYN BLD"\n  *** INVENTORY (%d/%d) ***\n\n"RST,P.inv_size,MAX_INV);
    if(P.inv_size==0){printf("  Empty!\n");pause_p();return;}
    const char*ts[]={"Weapon","Armor ","Potion","Elixir","Rune  ","Key   "};
    for(int i=0;i<P.inv_size;i++){
        char eq=' ';
        if(i==P.weapon_eq||i==P.armor_eq||i==P.rune_eq)eq='E';
        printf("  [%c]"YLW"[%d]"RST" %s %-22s pwr:+%d qty:%d\n",
            eq,i+1,ts[P.inv[i].type],P.inv[i].name,P.inv[i].power,P.inv[i].qty);
    }
    printf(YLW"\n  [num]"RST" Equip/Use  "YLW"[0]"RST" Back\n"WHT"  > "RST);
    int c;scanf("%d",&c);while(getchar()!='\n');
    if(c<1||c>P.inv_size)return;
    int idx=c-1;Item*it=&P.inv[idx];
    if(it->type==IT_POTION){
        int h=it->power;if(h>P.max_hp-P.hp)h=P.max_hp-P.hp;
        P.hp+=h;printf(GRN"  Healed %d HP!\n"RST,h);
        it->qty--;if(it->qty==0){for(int j=idx;j<P.inv_size-1;j++)P.inv[j]=P.inv[j+1];P.inv_size--;}
    }else if(it->type==IT_ELIXIR){
        if(it->power>=100){P.hp=P.max_hp;P.mp=P.max_mp;printf(GRN"  Full restore!\n"RST);}
        else if(it->power==50){P.mp+=50;if(P.mp>P.max_mp)P.mp=P.max_mp;printf(BLU"  Mana restored!\n"RST);}
        else{P.atk+=it->power/10;printf(YLW"  ATK +%d!\n"RST,it->power/10);}
        it->qty--;if(it->qty==0){for(int j=idx;j<P.inv_size-1;j++)P.inv[j]=P.inv[j+1];P.inv_size--;}
    }else if(it->type==IT_WEAPON){
        if(P.weapon_eq>=0)P.atk-=P.inv[P.weapon_eq].power;
        P.weapon_eq=idx;P.atk+=it->power;printf(GRN"  Equipped %s! ATK+%d\n"RST,it->name,it->power);
    }else if(it->type==IT_ARMOR){
        if(P.armor_eq>=0)P.def-=P.inv[P.armor_eq].power;
        P.armor_eq=idx;P.def+=it->power;printf(GRN"  Equipped %s! DEF+%d\n"RST,it->name,it->power);
    }else if(it->type==IT_RUNE){
        if(P.rune_eq>=0)P.speed-=P.inv[P.rune_eq].power;
        P.rune_eq=idx;P.speed+=it->power;printf(GRN"  Equipped %s! SPD+%d\n"RST,it->name,it->power);
    }
    pause_p();
}

void quests_menu(void){
    cls();printf(CYN BLD"\n  *** QUEST BOARD ***\n\n"RST);
    for(int i=0;i<P.quest_count;i++){
        Quest*q=&P.quests[i];
        const char*st;
        if(q->claimed)st=GRN"Claimed"RST;
        else if(q->done)st=YLW"CLAIMABLE!"RST;
        else st=DCYN"In Progress"RST;
        int pr=q->kills>q->target_kills?q->target_kills:q->kills;
        printf("  "YLW"[%d]"RST" %-35s %s\n",i+1,q->desc,st);
        if(!q->claimed)printf("      %d/%d kills | Reward: %dg +%d EXP\n\n",
            pr,q->target_kills,q->reward_gold,q->reward_exp);
    }
    printf(YLW"  [num]"RST" Claim  "YLW"[0]"RST" Back\n"WHT"  > "RST);
    int c;scanf("%d",&c);while(getchar()!='\n');
    if(c>=1&&c<=P.quest_count){
        Quest*q=&P.quests[c-1];
        if(q->done&&!q->claimed){
            P.gold+=q->reward_gold;gain_exp(q->reward_exp);q->claimed=1;
            if(q->target_kills>=20){P.gems+=2;printf(MAG"  Bonus: +2 gems!\n"RST);}
            printf(GRN"  Quest complete! +%dg +%d EXP\n"RST,q->reward_gold,q->reward_exp);
            if(P.quest_count<MAX_QUESTS){
                int nk=P.quests[P.quest_count-1].target_kills*2+rng(5,20);
                int qi=P.quest_count++;
                snprintf(P.quests[qi].desc,64,"Slay %d monsters",nk);
                P.quests[qi].target_kills=nk;
                P.quests[qi].reward_gold=nk*rng(18,28);
                P.quests[qi].reward_exp=nk*rng(14,22);}
        }else if(q->claimed)printf(DCYN"  Already claimed.\n"RST);
        else printf(RED"  Not done yet.\n"RST);
        pause_p();}
}

void arena(void){
    cls();
    printf(RED BLD"\n  *** ARENA GAUNTLET ***\n\n"RST);
    printf(DCYN"  Survive waves for huge rewards!\n"RST);
    printf("  Wins:"GRN"%d"RST"  Losses:"RED"%d\n\n"RST,P.arena_wins,P.arena_losses);
    printf(YLW"[1]"RST" Bronze (5 waves)  — 200g+3gems\n");
    printf(YLW"[2]"RST" Silver (10 waves) — 600g+8gems\n");
    printf(YLW"[3]"RST" Gold   (15 waves) — 1500g+20gems\n");
    printf(YLW"[4]"RST" NIGHTMARE(20 waves)— 5000g+50gems\n");
    printf(YLW"[0]"RST" Back\n\n"WHT"  > "RST);
    int c;scanf("%d",&c);while(getchar()!='\n');
    if(c<1||c>4)return;
    int waves[]={5,10,15,20};
    int gr[]={200,600,1500,5000};
    int gmr[]={3,8,20,50};
    int lr[]={1,10,20,35};
    if(P.level<lr[c-1]){printf(RED"  Need level %d!\n"RST,lr[c-1]);pause_p();return;}
    printf(YLW"\n  GAUNTLET BEGINS! %d waves!\n"RST,waves[c-1]);pause_p();
    int survived=0;
    for(int wave=1;wave<=waves[c-1];wave++){
        int bi=P.level-3+rng(0,5);
        if(bi<0)bi=0;if(bi>=50)bi=49;
        Enemy E=ENEMIES[bi];
        E.hp=(int)(E.hp*(1.0+wave*0.1));
        E.atk=(int)(E.atk*(1.0+wave*0.05));
        int e_hp=E.hp;
        printf(YLW"\n  --- Wave %d/%d: %s %s ---\n"RST,wave,waves[c-1],E.sym,E.name);
        int dead=0;
        while(e_hp>0&&P.hp>0){
            printf("  HP:%d/%d MP:%d/%d | "YLW"[1]"RST"Atk "YLW"[2]"RST"PWR "YLW"[3]"RST"Pot\n"RST,P.hp,P.max_hp,P.mp,P.max_mp);
            printf(WHT"> "RST);int a;scanf("%d",&a);while(getchar()!='\n');
            if(a==1){int d=rng(P.atk-2,P.atk+6)-rng(0,E.def/2);if(d<1)d=1;
                if(rng(1,100)<=15){d=(int)(d*1.7);printf(YLW"  CRIT!\n"RST);}
                e_hp-=d;printf(GRN"  Hit %d! Enemy HP:%d\n"RST,d,e_hp>0?e_hp:0);
            }else if(a==2){if(P.mp>=10){P.mp-=10;int d=rng(P.atk+4,P.atk+14);e_hp-=d;printf(MAG"  PWR:%d!\n"RST,d);}else printf(RED"  No MP!\n"RST);
            }else if(a==3)use_potion_in_battle();
            if(e_hp>0){int ed=rng(E.atk-2,E.atk+3)-rng(0,P.def/2);if(ed<1)ed=1;
                if(P.class_type==CL_PALADIN)ed=(int)(ed*0.8);
                P.hp-=ed;printf(RED"  %s hits -%d!\n"RST,E.name,ed);}
            if(P.hp<=0){dead=1;break;}
        }
        if(dead){printf(RED"\n  Defeated on wave %d!\n"RST,wave);break;}
        int wg=rng(E.gold_min,E.gold_max)+wave*5;P.gold+=wg;
        gain_exp(E.exp_reward);P.total_kills++;P.kills++;
        printf(GRN"  Wave %d cleared! +%dg\n"RST,wave,wg);
        survived=wave;
        P.hp+=P.max_hp/5;if(P.hp>P.max_hp)P.hp=P.max_hp;
        P.mp+=P.max_mp/4;if(P.mp>P.max_mp)P.mp=P.max_mp;
        usleep(250000);
    }
    if(survived==waves[c-1]){
        P.gold+=gr[c-1];P.gems+=gmr[c-1];P.arena_wins++;
        printf(YLW BLD"\n  GAUNTLET COMPLETE! +%dg +%d gems!\n"RST,gr[c-1],gmr[c-1]);
    }else{
        P.arena_losses++;
        int part=(int)(gr[c-1]*(survived/(float)waves[c-1])*0.5);
        P.gold+=part;printf(DYLW"  Partial reward: +%dg\n"RST,part);}
    pause_p();
}

void daily(void){
    printf(YLW BLD"\n  *** DAILY LOGIN REWARD! ***\n"RST);
    printf(DCYN"  Streak: %d days\n\n"RST,P.streak);
    int gold=100+P.streak*25;
    int gems=P.streak>=7?3:(P.streak>=3?1:0);
    P.gold+=gold;P.gems+=gems;P.streak++;
    printf(GRN"  +%dg"RST,gold);
    if(gems>0)printf(MAG"  +%d gems"RST,gems);
    if(P.streak==7)printf(YLW"\n  *** 7-Day Streak Bonus! ***"RST);
    if(P.streak==30)printf(RED"\n  *** 30-Day LEGEND Streak! ***"RST);
    printf(GRN"\n  Come back tomorrow for more!\n"RST);
    pause_p();
}

void prestige_menu(void){
    if(P.level<50){printf(RED"  Need level 50!\n"RST);pause_p();return;}
    cls();printf(RED BLD"\n  *** PRESTIGE SYSTEM ***\n\n"RST);
    printf(DCYN"  Reset to Lv.1, keep permanent bonuses!\n\n"RST);
    printf(YLW"  Current Prestige: %d\n"RST,P.prestige);
    printf(GRN"  Gain: +15 ATK, +20 DEF, +50 MaxHP, +20 gems\n\n"RST);
    printf(WHT"  Sure? (y/n): "RST);char c;scanf(" %c",&c);while(getchar()!='\n');
    if(c=='y'||c=='Y'){
        P.prestige++;P.level=1;P.exp=0;P.exp_next=100;
        P.atk+=15;P.def+=20;P.max_hp+=50;P.hp=P.max_hp;
        P.gems+=20;P.world_level=1;
        printf(MAG BLD"\n  PRESTIGE %d! Bonuses applied!\n"RST,P.prestige);
        save_g();pause_p();}
}

void stats_menu(void){
    cls();const char*cn[]={"Warrior","Mage","Rogue","Paladin"};
    printf(CYN BLD"\n  *** HERO STATS ***\n\n"RST);
    printf("  %s the %s (Prestige %d)\n",P.name,cn[P.class_type],P.prestige);
    printf("  Level: %d%s | World: %d/10\n",P.level,P.level==50?" MAX":"",P.world_level);
    printf("  Kills: %d | Deaths: %d | K/D: %.2f\n",
        P.total_kills,P.deaths,P.deaths>0?(float)P.total_kills/P.deaths:(float)P.total_kills);
    printf("  Arena: %dW/%dL | Streak: %d | Gold Earned: %ld\n",
        P.arena_wins,P.arena_losses,P.streak,P.total_gold_earned);
    printf("  ATK:%d DEF:%d SPD:%d HP:%d/%d MP:%d/%d\n",
        P.atk,P.def,P.speed,P.hp,P.max_hp,P.mp,P.max_mp);
    printf("  Weapon: %s\n",P.weapon_eq>=0?P.inv[P.weapon_eq].name:"None");
    printf("  Armor:  %s\n",P.armor_eq>=0?P.inv[P.armor_eq].name:"None");
    printf("  Rune:   %s\n",P.rune_eq>=0?P.inv[P.rune_eq].name:"None");
    pause_p();
}

int main(void){
    srand((unsigned)time(NULL));
    cls();banner();
    printf(CYN"  [1]"RST" New Game\n");
    printf(CYN"  [2]"RST" Continue\n");
    printf(CYN"  [3]"RST" Quit\n");
    printf(WHT"  > "RST);
    int c;scanf("%d",&c);while(getchar()!='\n');
    if(c==3){printf(YLW"\n  Goodbye!\n"RST);return 0;}
    if(c==2){
        if(!load_g()){printf(RED"  No save found!\n"RST);usleep(800000);new_game();}
        else{printf(GRN"\n  Welcome back, %s!\n"RST,P.name);daily();}
    }else{new_game();daily();}

    while(running){
        cls();hud();
        printf(CYN"  =========================================\n"RST);
        printf(YLW"  [1]"RST" Hunt Monsters\n");
        printf(YLW"  [2]"RST" Arena Gauntlet\n");
        printf(YLW"  [3]"RST" Shop\n");
        printf(YLW"  [4]"RST" Inventory & Equip\n");
        printf(YLW"  [5]"RST" Quests\n");
        printf(YLW"  [6]"RST" Statistics\n");
        printf(YLW"  [7]"RST" Prestige (Lv.50)\n");
        printf(YLW"  [8]"RST" Save Game\n");
        printf(YLW"  [9]"RST" Quit\n");
        printf(CYN"  =========================================\n"RST);
        printf(WHT"  Choice: "RST);
        int ch;scanf("%d",&ch);while(getchar()!='\n');
        switch(ch){
            case 1:go_hunt();break;
            case 2:arena();break;
            case 3:shop_menu();break;
            case 4:inv_menu();break;
            case 5:quests_menu();break;
            case 6:stats_menu();break;
            case 7:prestige_menu();break;
            case 8:save_g();pause_p();break;
            case 9:save_g();printf(YLW"\n  Farewell, %s!\n\n"RST,P.name);running=0;break;
            default:printf(RED"  Invalid.\n"RST);break;
        }
    }
    return 0;
}

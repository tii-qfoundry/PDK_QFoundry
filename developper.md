
## Class Architecture


### Junctions
```
└── Element
  └── Junction
    └─── Squid
      ├── Manhattan
    ├── Manhattan Single Jucntion
    ├── No squid
    ├── Sim 
    ├── ** Starfish manhattan **
```

### Chips
A chip is an Element type that inludes multiple other objects including launchers, alignement marks, and any other element, and may refer to layer specifications that apply to more than one layer. 
```
└── Element
  └── Chips
    ├── Chip
    ├── Empty
    ├── Launchers
    ├── ** Starfish Francisco **
  
```

### Development
Standalone library with geometries only, using layer specification for the QFoundry only. Each PCell in this library has (or will have) and homologue in one of the KQcircuits libraries with full compatibiity.
```
├── ** Starfish manhattan **
```

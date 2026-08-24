|        | HunanNext | GenerationInstrumentalT&C | Tech.Co., | Ltd. |
| ------ | --------- | ------------------------- | --------- | ---- |
| N83624 | Series    | Programming               | Guide     |      |
|        | SCPI      | Protocol                  |           |      |
©CopyrightHunanNextGenerationInstrumentalT&CTech.Co.,Ltd.
Version:V20240130
l
NGI NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
Contents
CONTENTS..............................................................................................................1
1PREFACE...............................................................................................................1
2SAFETYINSTRUCTIONS.........................................................................................2
2.1SafetyNotes.....................................................................................................2
2.2SafetySymbols.................................................................................................2
3OVERVIEW...........................................................................................................3
4COMMUNICATIONCONFIGURATION....................................................................3
5PROGRAMMINGCOMMANDOVERVIEW............................................................. 3
5.1BriefIntroduction.............................................................................................3
5.2Syntax...............................................................................................................4
5.2.1CommandKeyword...............................................................................5
5.2.2CommandSeparator.............................................................................5
5.2.3Query....................................................................................................6
5.2.4CommandTerminator...........................................................................6
5.3ParameterFormat............................................................................................7
6COMMANDS........................................................................................................7
6.1IEEE488.2CommonCommands......................................................................7
6.2MeasureCommands........................................................................................8
6.3OutputCommands.........................................................................................11
6.4SourceCommands.........................................................................................14
6.5ChargeCommands.........................................................................................15
6.6SOCCommands..............................................................................................18
6.7SEQCommands..............................................................................................23
6.8Protection......................................................................................................30
6.9CANSetting....................................................................................................32
6.10FaultSimulation(Optional)..........................................................................34
6.11SetupInterfaceBoardDisconnection..........................................................34
6.12SystemCommands.......................................................................................35
7PROGRAMMINGEXAMPLES...............................................................................38
7.1SourceMode..................................................................................................38
7.2ChargeMode..................................................................................................38
7.3SOCTest.........................................................................................................39
7.4SEQMode......................................................................................................40
7.5Measurement.................................................................................................41
7.6FactoryReset..................................................................................................41
8ERRORINFORMATION........................................................................................41
NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

| HunanNext | GenerationInstrumentalT&C | Tech.Co., | Ltd. |
| --------- | ------------------------- | --------- | ---- |
8.1CommandError..............................................................................................41
8.2ExecutionError...............................................................................................44
l
NGI NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
1 Preface
DearCustomers,
First of all, we greatly appreciate your choice of N83624 series battery simulator
(N83624 for short). We are also honored to introduce our company, Hunan Next
GenerationInstrumentalT&CTech.Co.,Ltd.(NGIforshort).
AboutCompany
NGI is a professional manufacturer of intelligent equipment and test & control
instruments, mainly engaged in design, production, sales, installations and
maintenanceofinstrumentsandmeters,electronicproducts,mechanicalequipment,
automatictestsystems,computersoftware,automaticcontrolequipment,automatic
monitoringandalarmsystems.
NGI maintains close cooperation with many universities and scientific research
institutions, and maintains close ties with many industry leaders. We strive to
develop high-quality, technology-leading products, provide high-end technologies,
andcontinuetoexplorenewindustrymeasurementandcontrolsolutions.
AboutManual
This manual is applied to N83624 series battery simulator, including programming
guidebasedonstandardSCPIprotocol.ThecopyrightofthemanualisownedbyNGI.
Due to the upgrade of instrument, this manual may be revised without notice in
futureversions.
This manual has been reviewed carefully by NGI for the technical accuracy. The
manufacturer declines all responsibility for possible errors in this operation manual,
if due to misprints or errors in copying. The manufacturer is not liable for
malfunctioningiftheproducthasnotcorrectlybeenoperated.
To ensure the safety and correct use of N83624, please read this manual carefully,
especiallythesafetyinstructions.
Pleasekeepthismanualforfutureuse.
Thanksforyourtrustandsupport.
1 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

|          |              | HunanNext | GenerationInstrumentalT&C |     | Tech.Co., | Ltd. |
| -------- | ------------ | --------- | ------------------------- | --- | --------- | ---- |
| 2 Safety | Instructions |           |                           |     |           |      |
In the operation and maintenance of the instrument, please strictly comply with the
following safety instructions. Any performance regardless of attentions or specific
warnings in other chapters of the manual may impair the protective functions
providedbytheinstrument.
NGIshallnotbeliablefortheresultscausedbytheneglectofthoseinstructions.
| 2.1 Safety | Notes |     |     |     |     |     |
| ---------- | ----- | --- | --- | --- | --- | --- |
 ConfirmtheACinputvoltagebeforesupplyingpower.
 Reliable grounding: Beforeoperation, the instrument mustbe reliablygrounded
toavoidtheelectricshock.

Confirmthefuse:Ensuretohaveinstalledthefusecorrectly.

Do not open the chassis: The operator cannot open the instrument chassis.
Non-professionaloperatorsarenotallowedtomaintainoradjustit.
 Do not operate under hazardous conditions: Do not operate the instrument
underflammableorexplosiveconditions.
 Confirmtheworkingrange:MakesuretheDUTiswithinN83624’sratedrange.
| 2.2 Safety | Symbols |     |     |     |     |     |
| ---------- | ------- | --- | --- | --- | --- | --- |
Please refer to the following table for definitions of international symbols used on
theinstrumentorintheusermanual.
Table1
| Symbol  |                        | Definition | Symbol |                       | Definition  |     |
| ------- | ---------------------- | ---------- | ------ | --------------------- | ----------- | --- |
|         | DC(directcurrent)      |            | N      | Nulllineorneutralline |             |     |
|         | AC(alternatingcurrent) |            | L      | Liveline              |             |     |
|         | ACandDC                |            | I      | Power-on              |             |     |
|         | Three-phasecurrent     |            |        | Power-off             |             |     |
|         | Ground                 |            |        | Back-uppower          |             |     |
|         | Protectiveground       |            |        | Power-onstate         |             |     |
|         | Chassisground          |            |        | Power-offstate        |             |     |
|         | Signalground           |            |        | Riskofelectricshock   |             |     |
|         |                        |            |        | High                  | temperature |     |
| WARNING | Hazardoussign          |            |        |                       |             |     |
warning
| Caution | Becareful |                                              |     | Warning |     |     |
| ------- | --------- | -------------------------------------------- | --- | ------- | --- | --- |
| 2       |           | l                                            |     |         |     |     |
|         | NGI       | NGI N83624SeriesProgrammingGuideSCPIProtocol |     |         |     |     |

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
3 Overview
N83624 series battery simulators provide LAN port and RS232 interface. Users can
connectN83624andPCbythecorrespondingcommunicationlinetorealizecontrol.
4 Communication Configuration
Communicationprotocol:standardSCPI
Communicationmethod:LAN,RS232
DefaultIPaddress:192.168.0.123(Itcanbeadjusted.Itwilltakeeffectafterrestart.)
UDPportnumber:7000-7024
Note: Port7000 iscommunication board, which canalso control 24channels. Port7001
to 7024 corresponds to channel 1 to 24. It is recommended that users who have
requirementsfordatacollectionspeedcommunicatethroughports7001-7024.
TCPportnumber:7000
Defaultbaudrate:115200(Itcanbeadjusted.Itwilltakeeffectafterrestart.)
5 Programming Command Overview
5.1 Brief Introduction
N83624 commands include two types: IEEE488.2 public commands and SCPI
commands.
IEEE488.2publiccommandsdefinesomecommoncontrolandquerycommandsfor
instruments. Basic operation on N83624 can be achieved through public commands,
suchasreset,statusquery,etc.AllIEEE488.2publiccommandsconsistofanasterisk
(*)andthree-lettermnemonic:*RST,*IDN?,*OPC?,etc.
SCPIcommandscanimplementmostofN83624functionsoftesting,setting,
calibration and measurement. SCPI commands are organized in the form of a
command tree. Each command can contain multiple mnemonics, and each node of
the command tree is separated by a colon (:), as shown in the below figure. Top of
the command tree is called ROOT. The full path from ROOT to the leaf node is a
completeprogrammingcommand.
3 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
Figure1 CommandTreeExample
5.2 Syntax
N83624 SCPIcommandsarethe inheritance andexpansionofIEEE 488.2 commands.
SCPI commands consist of command keywords, separators, parameter fields and
terminators.Takethefollowingcommandasanexample:
SOURce<n>:VOLTage2.5
Inthiscommand,SOURce andVOLTagearecommandkeywords.nischannelnumber
1 to 24. The colon (:) and space are separators. 2.5 is the parameter field. The
carriage return is terminator. Some commands have multiple parameters. The
parametersareseparatedbyacomma(,).
MEASure:VOLTage?(@1,2)
This command means obtaining readback voltage of channel 1 and 2. Number 1 and
2meanschannelnumber,whichareseparatedbyacomma.
Readingreadbackvoltageof24channelsatthesametime:
MEASure:VOLTage?(@1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24
)
Writingconstantvoltagevalueto5Vof24channelsatthesametime:
SOURce:VOLTage
5(@1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24)
For the convenience of description, the symbols in the subsequent chapters will be
applicabletothefollowingconventions.
 Square brackets ([]) indicate optional keywords or parameters, which can be
4 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
omitted.
 Curlybrackets({})indicatetheparameteroptionsinthecommandstring.
 Anglebrackets(<>)indicatethatanumericparametermustbeprovided.
 The vertical line (|) is used to separate the options of multiple optional
parameters.
5.2.1 Command Keyword
Each command keyword has two formats: long mnemonic and short mnemonic.
Short mnemonic is short for long mnemonic. Each mnemonic should not exceed 12
characters, including any possible numeric suffixes. The battery simulator only
acceptspreciselylongorshortmnemonics.
Therulesforgeneratingmnemonicsareasfollows:
1. Long mnemonics consist of one word or phrase. If it is a word, the entire word
constitutesamnemonic.
Examples:
CURRENT —— CURRent
2. Shortmnemonicsgenerallyconsistofthefirst4charactersoflongmnemonics.
Example:
CURRent —— CURR
3. Ifthecharacter lengthoflong mnemonicislessthanorequal to4, long andshort
mnemonicsare the same. If the character length of long mnemonic is greater than 4
and the fourth character is a vowel, short mnemonic will be composed of 3
characters,discardingthevowel.
Examples:
MODE —— MODE
POWer —— POW
4. Mnemonicsarenotcasesensitive.
5.2.2 Command Separator
1. Colon(:)
Colonisusedtoseparatetwoadjacentkeywordsinthecommand,suchasseparating
SOUR1andVOLTincommandSOUR1:VOLT2.54.
Colon can also be the first character of a command, indicating it will seek path from
thetopnodeofcommandtree.
5 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
2. Space
Spaceisusedtoseparatecommandfieldandparameterfield.
3. Semicolon(;)
Semicolon is used to separate multiple command units when multiple command
unitsareincludedinonecommand.Thelevelofthepresentpathdoesnotchangeby
usingasemicolon.
Example:
SOUR1:VOLT2.54;OUTCURR1000
The above command is to set constant voltage value to 2.54V and output current
limit to 1000mA in source mode. The above command is equivalent to the following
twocommands:
SOUR1:VOLT2.54
SOUR1:OUTCURR1000
4. SemicolonandColon(;:)
Itisusedtoseparatemultiplecommands.
MEASure:VOLTage?;:SOURce:VOLTage10;:OUTPut:ONOFF1
5.2.3 Query
Question mark (?) is used to mark the query function. It follows the last keyword of
thecommandfield.Forexample,forqueryingconstantvoltageofchannel1insource
mode,thequerycommandisSOUR1:VOLT?.Iftheconstantvoltageis5V, thebattery
simulatorwillreturnacharacterstring5.
After the batterysimulator receivesthe query command andcompletes the analysis,
it will execute the command and generate a response string. The response string is
firstwrittenintotheoutputbuffer.IfthepresentremoteinterfaceisaGPIBinterface,
it waits for the controller to read the response. Otherwise, it immediately sends the
responsestringtotheinterface.
Mostcommandshavecorrespondingquery syntax.If a commandcannotbequeried,
thebatterysimulatorwillreportanerrormessage-115Commandcannotqueryand
nothingwillbereturned.
5.2.4 Command Terminator
The command terminators are line feed character (ASCII character LF, value 10) and
EOI (only for GPIB interface). The terminator function is to terminate the present
6 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

|     |     |     | HunanNext | GenerationInstrumentalT&C |     |     | Tech.Co., | Ltd. |
| --- | --- | --- | --------- | ------------------------- | --- | --- | --------- | ---- |
commandstringandresetthecommandpathtotherootpath.
| 5.3 Parameter |     | Format |     |     |     |     |     |     |
| ------------- | --- | ------ | --- | --- | --- | --- | --- | --- |
Parameter programmed are represented by ASCII code in the types of numeric,
character,bool,etc.
Table2
| Symbol |                        |       | Description |               |        |                       | Example |     |
| ------ | ---------------------- | ----- | ----------- | ------------- | ------ | --------------------- | ------- | --- |
| <NR1>  | Integervalue           |       |             |               |        | 123                   |         |     |
| <NR2>  | Floatingpointvalue     |       |             |               |        | 123.,12.3,0.12,1.23E4 |         |     |
| <NRf>  | ThevaluemaybeNR1orNR2. |       |             |               |        |                       |         |     |
|        | Expanded               | value | format      | that includes | <NRf>, | MIN                   |         |     |
<NRf+>
andMAX.
| <Bool> | Booleandata                   |            |        |           |            | 1|0|ON|OFF |     |     |
| ------ | ----------------------------- | ---------- | ------ | --------- | ---------- | ---------- | --- | --- |
| <CRD>  | Characterdata,forexample,CURR |            |        |           |            |            |     |     |
|        | Return                        | ASCII code | data,  | allowing  | the return | of         |     |     |
| <AARD> | undefined                     | 7-bit      | ASCII. | This data | type has   | an         |     |     |
impliedcommandterminator.
6 Commands
| 6.1 IEEE | 488.2 | Common |     | Commands |     |     |     |     |
| -------- | ----- | ------ | --- | -------- | --- | --- | --- | --- |
Common commands are general commands required by IEEE 488.2 standard that
instruments must support. They are used to control the general functions of
instruments, such as reset and status query. Its syntax and semantics follow IEEE
488.2standard.IEEE488.2commoncommandshavenohierarchy.
*IDN?
This command reads information of the battery simulator. It returns the data in four
fields separated by commas. The data include manufacturer, model, reserved field
andsoftwareversion.
| QuerySyntax |     |     | *IDN?                                    |        |                 |     |     |     |
| ----------- | --- | --- | ---------------------------------------- | ------ | --------------- | --- | --- | --- |
| Parameters  |     |     | None                                     |        |                 |     |     |     |
| Returns     |     |     | <AARD>                                   | String | Description     |     |     |     |
|             |     |     |                                          | NGI    | Manufacturer    |     |     |     |
|             |     |     |                                          | N83624 | Model           |     |     |     |
|             |     |     |                                          | 0      | Reservedfield   |     |     |     |
|             |     |     |                                          | XX.XX  | Softwareversion |     |     |     |
| 7           |     | l   |                                          |        |                 |     |     |     |
|             | NGI | NGI | N83624SeriesProgrammingGuideSCPIProtocol |        |                 |     |     |     |

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
ReturnsExample NGI,N83624,0,V1.00
*OPC
This command sets the Operation Complete (OPC) bit in the Standard Event Register
to1whenalloperationsandcommandsarecompleted.
CommandSyntax *OPC
Parameters None
QuerySyntax *OPC?
Returns <NR1>
RelatedCommands *TRG
*RST
Thiscommandisusedtorestorefactorysettings.
CommandSyntax *RST
Parameters None
Returns None
RelatedCommands None
ExecutingtheFactoryResetcommandresetsthefollowingparametersofthedevice:
1.Resetsthevoltageandoutputcurrentlimitto0inpowermode;
2.Resetthevoltage,currentandinternalresistanceto0underchargingmode;
3.ResetfiletothedefaultfileunderSOCEdit;
4. Reset protection value (over-voltage, over-current, over-power protection, etc.) to
0;
5.Clearallthesequencerunningfiles,andsetSEQfilestepto0;
6.ResetCANIDtochannelID,baudrateto250K,andactiveuploadtimeto0.
7. Reset the device IP to 192.168.0.123, device ID to 1, serial port rate to 115200,
samplingspeedtomediumspeed,power-offmemoryoff.
Note: After restoring the factory settings, it takesabout 10s because it needsto save
thedatatothememory.
6.2 Measure Commands
MEASure<n>:CURRent?
Thiscommandqueriesthereadbackcurrentofcorrespondingchannel.
CommandSyntax MEASure<n>:CURRent?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
Example MEAS1:CURR?
8 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
Returns <NRf>
Unit mA
MEASure<n>:VOLTage?
Thiscommandqueriesthereadbackvoltageofcorrespondingchannel.
CommandSyntax MEASure<n>:VOLTage?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
Example MEAS1:VOLT?
Returns <NRf>
Unit V
MEASure<n>:POWer?
Thiscommandqueriesthereadbackpowerofcorrespondingchannel.
CommandSyntax MEASure<n>:POWer?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
Example MEAS1:POW?
Returns <NRf>
Unit W
9 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
MEASure<n>:MAH?
Thiscommandqueriesthecapacityofcorrespondingchannel.
CommandSyntax MEASure<n>:MAH?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
Example MEAS1:MAH?
Returns <NRf>
Unit mAh
MEASure<n>:Res?
Thiscommandqueriestheresistancevalueofcorrespondingchannel.
CommandSyntax MEASure<n>:Res?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
Example MEAS1:R?
Returns <NRf>
Unit mΩ
10 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
MEASure<n>:CAPRate?
Thiscommandqueriesthesense/samplingrate.
CommandSyntax MEASure<n>:CAPR<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom0to24.NR1
rangeis0|1|2.
Example MEAS1:CAPR1
QuerySyntax MEAS1:CAPR?
Returns 0for10ms,1for120ms,2for480ms
6.3 Output Commands
OUTPut<n>:MODE
Thiscommandisusedtosettheoperationmodeofcorrespondingchannel.
CommandSyntax OUTPut<n>:MODE<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:0|1|3|128
Example OUTP1:MODE1
QuerySyntax OUTP1:MODE?
Returns 0forsourcemode
1forchargemode
3forSOCmode
11 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
128forSEQmode
OUTPut<n>:ONOFF
Thiscommandturnsonorofftheoutputofcorrespondingchannel.
CommandSyntax OUTPut<n>:ONOFF<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:1|0
Example OUTP1:ONOFF1
QuerySyntax OUTP1:ONOFF?
Returns 1forON
0forOFF
OUTPut<n>:STATe?
Thiscommandqueriesoperatingstateofcorrespondingchannel.
CommandSyntax OUTPut<n>:STATe?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax OUTP1:STAT?
Returns Channelstate
Bit0：ON/OFFstate
Bit1：ovp（overvoltageprotection）
Bit2：ocp（overcurrentprotection）
Bit3：opp（overpowerprotection）
Bit4：otp（overtemperatureprotection）
Bit5：ofp（Voltageandcurrentpresentatportwhenoperating
12 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
faultsimulationrelay）
Bit6：omp（Allowsoperationoffaultsimulationrelaysinpower
modeonly,othermodesarenotsupported.）
Bit16-18：readbackvaluerange,0forhighrange,1formedium
range,2forlowrange
OUTPut<n>:EVENt?
Thiscommandquerieschannelevent.
CommandSyntax OUTPut<n>:EVENt?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax OUTP1:EVENt?
Returns Channelstate
Bit0：ON/OFFstate
Bit1：ovp（overvoltageprotection）
Bit2：ocp（overcurrentprotection）
Bit3：opp（overpowerprotection）
Bit4：otp（overtemperatureprotection）
Bit5：ofp（Voltageandcurrentpresentatportwhenoperating
faultsimulationrelay）
Bit6：omp（Allowsoperationoffaultsimulationrelaysinpower
modeonly,othermodesarenotsupported.）
Bit16-18：readbackvaluerange,0forhighrange,1formedium
range,2forlowrange
13 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
OUTPut<n>:ONDWell
Thiscommandturnsondwellofcorrespondingchannel.
CommandSyntax OUTPut<n>:ONDWell<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:0~0xfffffffe
Example OUTP1:ONDWell250000
QuerySyntax OUTP1:ONDWell?
Returns 250000;unitus
6.4 Source Commands
SOURce<n>:VOLTage
Thiscommandisusedtosetoutputconstantvoltage.
CommandSyntax SOURce<n>:VOLTage<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SOUR1:VOLT2.54
QuerySyntax SOUR1:VOLT?
Returns <NRf>
Unit V
SOURce<n>:OUTCURRent
Thiscommandisusedtosetoutputcurrentlimit.
14 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
CommandSyntax SOURce<n>:OUTCURRent<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SOUR1:OUTCURR1000
QuerySyntax SOUR1:OUTCURR?
Returns <NRf>
Unit mA
SOURce<n>:RANGe
Thiscommandisusedtosetcurrentrange.
CommandSyntax SOURce<n>:RANGe<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:0|2|3
Example SOUR1:RANG1
QuerySyntax SOUR1:RANG?
Returns 0forhighrange
2forlowrange
3forautorange
6.5 Charge Commands
CHARge<n>:VOLTage
Thiscommandisusedtosetoutputconstantvoltageunderchargemode.
15 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
CommandSyntax CHARge<n>:VOLTage<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example CHAR1:VOLT5.6
QuerySyntax CHAR1:VOLT?
Returns <NRf>
Unit V
CHARge<n>:OUTCURRent
Thiscommandisusedtosetoutputcurrentlimitunderchargemode.
CommandSyntax CHARge<n>:OUTCURRent<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example CHAR1:OUTCURR2000
QuerySyntax CHAR1:OUTCURR?
Returns <NRf>
Unit mA
CHARge<n>:Res
Thiscommandisusedtosetresistancevalueunderchargemode.
16 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
CommandSyntax CHARge<n>:Res<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example CHAR1:R0.2
QuerySyntax CHAR1:R?
Returns <NRf>
Unit mΩ
CHARge<n>:ECHO:VOLTage?
Thiscommandqueriesreadbackvoltageunderchargemode.
CommandSyntax CHARge<n>:ECHO:VOLTage
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
Example CHAR1:ECHO:VOLTage?
Returns <NRf>
Unit V
CHARge<n>:ECHO:Q?
Thiscommandqueriesreadbackcapacityunderchargemode.
CommandSyntax CHARge<n>:ECHO:Q
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
17 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
Example CHAR1:ECHO:Q?
Returns <NRf>
Unit mAh
6.6 SOC Commands
SOC<n>:EDIT:FILE
Thiscommandisusedtosetthetotaloperationsteps.
CommandSyntax SOC<n>:EDIT:RILE<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:1-8
Example SOC1:EDIT:FILE3
QuerySyntax SOC1:EDIT:FILE?
Returns <NR1>
SOC<n>:EDIT:LENGth
Thiscommandisusedtosetthetotaloperationsteps.
CommandSyntax SOC<n>:EDIT:LENGth<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:0-200
Example SOC1:EDIT:LENG3
18 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
QuerySyntax SOC1:EDIT:LENG?
Returns <NR1>
SOC<n>:EDIT:STEP
Thiscommandisusedtosetthespecificstepnumber.
CommandSyntax SOC<n>:EDIT:STEP<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:1-200
Example SOC1:EDIT:STEP1
QuerySyntax SOC1:EDIT:STEP?
Returns <NR1>
SOC<n>:EDIT:VOLTage
Thiscommandisusedtosetvoltagevalueforthestepunderediting.
CommandSyntax SOC<n>:EDIT:VOLTage<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SOC1:EDIT:VOLT2.8
QuerySyntax SOC1:EDIT:VOLT?
Returns <NRf>
Unit V
19 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SOC<n>:EDIT:OUTCURRent
Thiscommandisusedtosetoutputcurrentlimitforthestepunderediting.
CommandSyntax SOC<n>:EDIT:OUTCURRent<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SOC1:EDIT:OUTCURR1000
QuerySyntax SOC1:EDIT:OUTCURR?
Returns <NRf>
Unit mA
SOC<n>:EDIT:Res
Thiscommandisusedtosetresistancevalueforthestepunderediting.
CommandSyntax SOC<n>:EDIT:Res<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SOC1:EDIT:R0.8
QuerySyntax SOC1:EDIT:R?
Returns <NRf>
Unit mΩ
20 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SOC<n>:EDIT:Q?
Thiscommandisusedtosetthecapacityforthestepunderediting.
CommandSyntax SOC<n>:EDIT:Q<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SOC1:EDIT:Q100
QuerySyntax SOC1:EDIT:Q?
Returns <NRf>
Unit mAh
SOC<n>:EDIT:SVOLtage
Thiscommandisusedtosettheinitial/startvoltage.
CommandSyntax SOC<n>:EDIT:SVOLtage<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SOC1:EDIT:SVOL0.8
QuerySyntax SOC1:EDIT:SVOL?
Returns <NRf>
Unit V
21 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SOC<n>:RUN:STEP?
Thiscommandisusedtoquerythepresentrunningstep.
CommandSyntax SOC<n>:RUN:STEP?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax SOC1:RUN:STEP?
Returns <NR1>
SOC<n>:RUN:Q?
Thiscommandisusedtoquerythepresentcapacityforthepresentrunningstep.
CommandSyntax SOC<n>:RUN:Q?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax SOC1:RUN:Q?
Returns <NRf>
Unit mAh
SOC<n>:OPEN:VOLTage?
Thiscommandisusedtoqueryopenvoltageforthepresentrunningstep.
CommandSyntax SOC<n>:OPEN:VOLTage?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
22 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
QuerySyntax SOC1:OPEN:VOLTage?
Returns <NRf>
SOC<n>:SIM:RES?
Thiscommandisusedtoquerysimulationinternalresistanceforthepresentrunning
step.
CommandSyntax SOC<n>:SIM:RES?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax SOC1:SIM:RES?
Returns <NRf>
6.7 SEQ Commands
SEQuence<n>:EDIT:FILE
Thiscommandisusedtosetsequencefilenumber.
CommandSyntax SEQuence<n>:EDIT:FILE<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:filenumber1to10
Example SEQ1:EDIT:FILE3
QuerySyntax SEQ1:EDIT:FILE?
23 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
Returns <NR1>
SEQuence<n>:EDIT:LENGth
Thiscommandisusedtosettotalstepsinthesequencefile.
CommandSyntax SEQuence<n>:EDIT:LENGth<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:0～200
Example SEQ1:EDIT:LENG20
QuerySyntax SEQ1:EDIT:LENG?
Returns <NR1>
SEQuence<n>:EDIT:STEP
Thiscommandisusedtosetthespecificstepnumber.
CommandSyntax SEQuence<n>:EDIT:STEP<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:1～200
Example SEQ1:EDIT:STEP5
QuerySyntax SEQ1:EDIT:STEP?
Returns <NR1>
24 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SEQuence<n>:EDIT:CYCle
Thiscommandisusedtosetthecycletimesforthefileunderediting.
CommandSyntax SEQuence<n>:EDIT:CYCle<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:0～100
Example SEQ1:EDIT:C0
QuerySyntax SEQ1:EDIT:C?
Returns <NR1>
SEQuence<n>:EDIT:VOLTage
Thiscommandisusedtosettheoutputvoltageforthestepunderediting.
CommandSyntax SEQuence<n>:EDIT:VOLTage<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SEQ1:EDIT:VOLT5
QuerySyntax SEQ1:EDIT:VOLT?
Returns <NRf>
Unit V
25 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SEQuence<n>:EDIT:OUTCURRent
Thiscommandisusedtosettheoutputcurrentlimitforthestepunderediting.
CommandSyntax SEQuence<n>:EDIT:OUTCURRent<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SEQ1:EDIT:OUTCURR500
QuerySyntax SEQ1:EDIT:OUTCURR?
Returns <NRf>
Unit mA
SEQuence<n>:EDIT:Res
Thiscommandisusedtosettheresistanceforthestepunderediting.
CommandSyntax SEQuence<n>:EDIT:Res<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SEQ1:EDIT:R0.4
QuerySyntax SEQ1:EDIT:R?
Returns <NRf>
Unit mΩ
26 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SEQuence<n>:EDIT:RUNTime
Thiscommandisusedtosettherunningtimeforthestepunderediting.
CommandSyntax SEQuence<n>:EDIT:RUNTime<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRf Range:MIN～MAX
Example SEQ1:EDIT:RUNT5
QuerySyntax SEQ1:EDIT:RUNT?
Returns <NRf>
Unit s
SEQuence<n>:EDIT:LINKStart
Thiscommandisusedtosettherequiredlinkstartstepafterthepresentstepis
completed.
CommandSyntax SEQuence<n>:EDIT:LINKStart<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:-1～200
Example SEQ1:EDIT:LINKS-1
QuerySyntax SEQ1:EDIT:LINKS?
Returns <NR1>
27 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SEQuence<n>:EDIT:LINKEnd
Thiscommandisusedtosetthelinkstopstepforthestepunderediting.
CommandSyntax SEQuence<n>:EDIT:LINKEnd<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:-1～200
Example SEQ1:EDIT:LINKE-1
QuerySyntax SEQ1:EDIT:LINKE?
Returns <NR1>
SEQuence<n>:EDIT:LINKCycle
Thiscommandisusedtosetcycletimesforthelink.
CommandSyntax SEQuence<n>:EDIT:LINKCycle<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:0～100
Example SEQ1:EDIT:LINKC5
QuerySyntax SEQ1:EDIT:LINKC?
Returns <NR1>
SEQuence<n>:RUN:FILE
Thiscommandisusedtosetthesequencetestfilenumber.
28 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
CommandSyntax SEQuence:RUN:FILE<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1 Range:filenumber1to10
Example SEQ1:RUN:FILE3
QuerySyntax SEQ1:RUN:FILE?
Returns <NR1>
SEQuence<n>:RUN:STEP？
Thiscommandisusedtoquerythepresentrunningstepnumber.
CommandSyntax SEQuence<n>:RUN:STEP?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax SEQ1:RUN:STEP?
Returns <NR1>
SEQuence<n>:RUN:Cycle
Thiscommandisusedtoquerythesequencerunningcycles.
CommandSyntax SEQuence<n>:EDIT:Cycle?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax SEQ1:RUN:C?
29 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
Returns <NR1>
SEQuence<n>:RUN:Time?
Thiscommandisusedtoquerytherunningtimeforthesequencetestfile.
CommandSyntax SEQuence<n>:RUN:Time?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax SEQ1:RUN:T?
Returns <NRf>
Unit s
6.8 Protection
PRO<n>:CURRent
ThiscommandisusedtoquerytheOCPcurrent.
CommandSyntax PRO<n>:CURRent<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRfrange:MIN～MAX
Sample PRO1:CURR1000
QuerySyntax PRO1:CURR?
Returns <NRf>
Unit mA
30 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
PRO<n>:VOLTage
ThiscommandisusedtoquerytheOVPvoltage.
CommandSyntax PRO<n>:VOLTage<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRfrange:MIN～MAX
Sample PRO1:VOLT5
QuerySyntax PRO1:VOLT?
Returns <NRf>
Unit V
PRO<n>:POWEr
ThiscommandisusedtoquerytheOPPpower.
CommandSyntax PRO<n>:POWEr<NRf>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NRfrange:MIN～MAX
Sample PRO1:POWE3000
QuerySyntax PRO1:POWE?
Returns <NRf>
Unit mW
31 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
6.9 CAN Setting
CFG<n>:CANID?
ThiscommandisusedtoqueryCANID.
CommandSyntax CFG<n>:CANID?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax CFG1:CANID?
Returns <NR1>
Default CHID,1to24
Note: When changing CAN setting, users need to turn on power-off memory first,
andthenrebootthedeviceaftermodifyingtheCANsettingparameters.
CFG<n>:UPTime
Thiscommandisusedtosetactiveuploadtime.
CommandSyntax CFG<n>:UPTime<NR1>
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
NR1range:0foroff,minimumtimeintervalover60
Sample CFG1:UPT60
QuerySyntax CFG1:UPT?
Returns <NR1>
Unit ms
32 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
CFG<n>:CANRate?
ThiscommandisusedtosetCANbaudrate.
CommandSyntax CFG<n>:CANRate?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax CFG1:CANR?
Returns <NR1>
CFG<n>:EXTCanid?
ThiscommandisusedtoqueryextensionIDaddress.
CommandSyntax CFG<n>:EXTCanid?
Parameters <n> Nreferstochannelnumber.Therangeisfrom1to24.
QuerySyntax CFG1:CANR?
Returns <NR1>
33 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

|            |            | HunanNext  | GenerationInstrumentalT&C | Tech.Co., | Ltd. |
| ---------- | ---------- | ---------- | ------------------------- | --------- | ---- |
| 6.10 Fault | Simulation | (Optional) |                           |           |      |
Thiscommandisusedtosetfaultsimulation.
| CommandSyntax | FAULt<n>:SIMUlate<NR1> |                                             |     |     |     |
| ------------- | ---------------------- | ------------------------------------------- | --- | --- | --- |
| Parameters    | <n>                    | Nreferstochannelnumber.Therangeisfrom1to24. |     |     |     |
| Example       | FAULt1:SIMUlate0       |                                             |     |     |     |
| QuerySyntax   | FAULt1:SIMUlate?       |                                             |     |     |     |
| Returns       | <NR1>                  |                                             |     |     |     |
0forNormal
1forOpenpositive
4forOpennegative
8forOutputshorted
96forReversepolarity
Note: Fault simulation is only allowed to operate in power mode, other modes are
not supported, otherwise the Bit6 bit omp of the channel event return value will be
setto1;
Please make sure that there is no voltage or current at the port when starting fault
simulation; it is recommended to turn off the output first and wait until the voltage
or current is 0 beforeoperating the fault simulation relay; otherwise, the Bit5 bit ofp
will be set to 1 to indicate that the user is not permitted to operate the fault
simulationrelayelectrically,soastopreventpermanentdamagetotherelay.
| 6.11 Setup | Interface | Board | Disconnection |     |     |
| ---------- | --------- | ----- | ------------- | --- | --- |
Thiscommandisusedtosetupinterfaceboarddisconnection.
| CommandSyntax | HMI:DISConnect:ENABle<NR1> |                                              |     |     |     |
| ------------- | -------------------------- | -------------------------------------------- | --- | --- | --- |
| QuerySyntax   | HMI:DISConnect:ENABle?     |                                              |     |     |     |
| 34            | l                          |                                              |     |     |     |
|               | NGI                        | NGI N83624SeriesProgrammingGuideSCPIProtocol |     |     |     |

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
Returns <NR1>
0-Disable;1-Enable
6.12 System Commands
SYSTem1:COMMand:LAN:IPADdr
ThiscommandisusedtosetIPaddress.
CommandSyntax SYSTem1:COMMand:LAN:IPADdr<NR1>
Parameters Dot-decimalrepresentation:e.g.IP192.168.0.123
Example SYSTem1:COMMand:LAN:IPADdr“192.168.0.123”
QuerySyntax SYSTem1:COMMand:LAN:IPADdr?
Returns 192.168.0.123
SYSTem1:COMMand:SERial:BAUDrate
Thiscommandisusedtosetseriesbaudrate.
CommandSyntax SYSTem1:COMMand:SERial:BAUDrate<NR1>
Parameters 9600/19200/38400/57600/115200
Example SYSTem1:COMMand:SERial:BAUDrate115200
QuerySyntax SYSTem1:COMMand:SERial:BAUDrate?
Returns 115200
35 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SYSTem1:SOUNd
Thiscommandisusedtosetbeeper.
CommandSyntax SYSTem1:SOUNd<NR1>
Parameters 0-OFF;1-ON
Example SYSTem1:SOUNd1
QuerySyntax SYSTem1:SOUNd?
Returns 1
SYSTem1:LANGuage
Thiscommandisusedtosetlanguage.
CommandSyntax SYSTem1:LANGuage<NR1>
Parameters 0-Chinese;1-English
Example SYSTem1:LANGuage0
QuerySyntax SYSTem1:LANGuage?
Returns 0
SYSTem1:COMMand:LAN:TYPe
Thiscommandisusedtosetconnectiontype.
CommandSyntax SYSTem1:COMMand:LAN:TYPe<NR1>
Parameters 0-UDP；1-TCP
Example SYSTem1:COMMand:LAN:TYPe0
36 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
QuerySyntax SYSTem1:COMMand:LAN:TYPe?
Returns 0
SYSTem1:POWDown:SAVe
ThiscommandisusedtosetpowerdownsaveON/OFF.
CommandSyntax SYSTem1:POWDown:SAVe<NR1>
Parameters 0-unsave;1-save
Example SYSTem1:POWDown:SAVe1
QuerySyntax SYSTem1:POWDown:SAVe?
Returns 1
37 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
7 Programming Examples
This chapter will describe how to control the battery simulator by programming
commands.
Note 1: In this chapter, there are comments starting with //, following some
commands. These comments cannot be recognized by the battery simulator, only
for the convenience of understanding the corresponding commands. Therefore, it
isnotallowedtoinputcommentsincluding//inpractice.
Note 2: There are 24 channels in total. For the below programming examples, it
demonstratesfunctionsofonlychannelnumberone.
7.1 Source Mode
UnderSourcemode,constantvoltageandcurrentlimitvaluecanbeset.
Example: set the battery simulator to Source mode, CV value to 5V, output current
limitto1000mAandcurrentrangetoAuto.
OUTPut1:ONOFF0 //turnofftheoutputforpresentchannel
OUTPut1:MODE0 //setoperationmodetoSourcemode
SOURce1:VOLTage5.0 //setCVvalueto5.0V
SOURce1:OUTCURRent1000 //setoutputcurrentlimitto1000mA
SOURce1:RANGe3 //select3-Autoforcurrentrange
OUTPut1:ONOFF1 //turnontheoutputforchannel1
7.2 Charge Mode
Under Charge mode, constant voltage, current limit and resistance value can be set.
Thecurrentrangeunderchargemodeisfixedashighrange.
Example: set the battery simulator to Charge mode, CV value to 5V, output current
limitto1000mAandresistancevalueto3.0mΩ.
OUTPut1:ONOFF0 //turnofftheoutputforpresentchannel
OUTPut1:MODE1 //setoperationmodetoChargemode
CHARge1:VOLTage5.0 //setCVvalueto5.0V
CHARge1:OUTCURRent1000 //setoutputcurrentlimitto1000mA
CHARge1:Res3.0 //setresistancevalueto3.0mΩ
OUTPut1:ONOFF1 //turnontheoutputforchannel1
38 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

|     |          |     | HunanNext | GenerationInstrumentalT&C |     | Tech.Co., | Ltd. |
| --- | -------- | --- | --------- | ------------------------- | --- | --------- | ---- |
| 7.3 | SOC Test |     |           |                           |     |           |      |
The main function of N83624 SOC test is to simulate battery discharge function.
Users need to input various parameters of battery discharge into the corresponding
channels, such as capacity, constant voltage value, output current limit, and
resistance value. The battery simulator judges whether the capacity difference of
present running step and the next step is equal, according to the capacity of present
running step. If equal, N83624 will move to next step. If not equal, N83624 will
continue to accumulate the capacity for present running step. The capacity is
determinedbytheconnectedDUT,thatis,theoutputcurrent.
Example:setthebatterysimulatortoSOCmode,totalstepsto3andinitialvoltageto
4.8V.Thestepsparametersareasbelowtable.
|                      | StepNo. | Capacity(mAh) |                                   | CVValue(V)                          | Current(mA) | Resistance(mΩ) |     |
| -------------------- | ------- | ------------- | --------------------------------- | ----------------------------------- | ----------- | -------------- | --- |
|                      | 1       | 1000          |                                   | 5.0                                 | 1000        | 0.1            |     |
|                      | 2       | 900           |                                   | 4.0                                 | 1000        | 0.2            |     |
|                      | 3       | 800           |                                   | 3.0                                 | 1000        | 0.3            |     |
| OUTPut1:ONOFF0       |         |               |                                   | //turnofftheoutputforpresentchannel |             |                |     |
| OUTPut1:MODE3        |         |               |                                   | //setoperationmodetoSOCmode         |             |                |     |
| SOC1:EDIT:LENGth     |         | 3             | //settotalstepsto3                |                                     |             |                |     |
| SOC1:EDIT:STEP1      |         |               | //setstepNo.to1                   |                                     |             |                |     |
| SOC1:EDIT:Q1200      |         |               | //setcapacityforstepNo.1to1200mAh |                                     |             |                |     |
| SOC1:EDIT:VOLTage5.0 |         |               | //setCVValueforstepNo.1to5.0V     |                                     |             |                |     |
SOC1:EDIT:OUTCURRent1000 //setoutputcurrentlimitforstepNo.1to1000mA
| SOC1:EDIT:Res0.1     |     |     | //setresistanceforstepNo.1to0.1mΩ |                               |     |     |     |
| -------------------- | --- | --- | --------------------------------- | ----------------------------- | --- | --- | --- |
| SOC1:EDIT:STEP2      |     |     |                                   | //setstepNo.to2               |     |     |     |
| SOC1:EDIT:Q900       |     |     | //setcapacityforstepNo.2to900mAh  |                               |     |     |     |
| SOC1:EDIT:VOLTage4.0 |     |     |                                   | //setCVValueforstepNo.2to4.0V |     |     |     |
SOC1:EDIT:OUTCURRent1000 //setoutputcurrentlimitforstepNo.2to1000mA
| SOC1:EDIT:Res0.2     |     |     | //setresistanceforstepNo.2to0.2mΩ |                                  |     |     |     |
| -------------------- | --- | --- | --------------------------------- | -------------------------------- | --- | --- | --- |
| SOC1:EDIT:STEP3      |     |     |                                   | //setstepNo.to3                  |     |     |     |
| SOC1:EDIT:Q800       |     |     |                                   | //setcapacityforstepNo.3to800mAh |     |     |     |
| SOC1:EDIT:VOLTage3.0 |     |     |                                   | //setCVValueforstepNo.3to3.0V    |     |     |     |
SOC1:EDIT:OUTCURRent1000 //setoutputcurrentlimitforstepNo.3to1000mA
| SOC1:EDIT:Res0.3  |     |     | //setresistanceforstepNo.3to0.3mΩ            |     |     |     |     |
| ----------------- | --- | --- | -------------------------------------------- | --- | --- | --- | --- |
| SOC1:EDIT:SVOL4.8 |     |     | //setinitial/startvoltageto4.8V              |     |     |     |     |
| OUTPut1:ONOFF1    |     |     | //turnontheoutputforchannel1                 |     |     |     |     |
| 39                |     | l   |                                              |     |     |     |     |
|                   |     | NGI | NGI N83624SeriesProgrammingGuideSCPIProtocol |     |     |     |     |

|               |     | HunanNext                              | GenerationInstrumentalT&C |     |     | Tech.Co., | Ltd. |
| ------------- | --- | -------------------------------------- | ------------------------- | --- | --- | --------- | ---- |
| SOC1RUN:STEP? |     | //readthepresentrunningstepNo.         |                           |     |     |           |      |
| SOC1:RUN:Q?   |     | //readthecapacityforpresentrunningstep |                           |     |     |           |      |
| 7.4 SEQ Mode  |     |                                        |                           |     |     |           |      |
The SEQ test mainly judges the number of running steps based on the selected SEQ
file. It will run all the steps in sequence, according to the preset output parameters
for each step. Links can also be made between steps. The corresponding cycle times
canbesetindependently.
Example: set the battery simulator to SEQ mode, SEQ file No. to 1, total steps to 3
andfilecycletimesto1.Thestepsparametersareasbelowtable.
| Step CV                   | Current(mA) | Resistance(mΩ) |                                     | Time(s) | Link  | Link | Link  |
| ------------------------- | ----------- | -------------- | ----------------------------------- | ------- | ----- | ---- | ----- |
| No. Value(V)              |             |                |                                     |         | Start | Stop | Cycle |
|                           |             |                |                                     |         | Step  | Step | Times |
| 1 1                       | 2000        |                | 0.0                                 | 5       | -1    | -1   | 0     |
| 2 2                       | 2000        |                | 0.1                                 | 10      | -1    | -1   | 0     |
| 3 3                       | 2000        |                | 0.2                                 | 20      | -1    | -1   | 0     |
| OUTPut1:ONOFF0            |             |                | //turnofftheoutputforpresentchannel |         |       |      |       |
| OUTPut1:MODE128           |             |                | //setoperationmodetoSEQmode         |         |       |      |       |
| SEQuence1:EDIT:FILE1      |             |                | //setSEQfileNo.to1                  |         |       |      |       |
| SEQuence1:EDIT:LENGth3    |             |                | //settotalstepsto3                  |         |       |      |       |
| SEQuence1:EDIT:CYCle1     |             |                | //setfilecycletimesto1              |         |       |      |       |
| SEQuence1:EDIT:STEP1      |             |                | //setstepNo.to1                     |         |       |      |       |
| SEQuence1:EDIT:VOLTage1.0 |             |                | //setCVValueforstepNo.1to1.0V       |         |       |      |       |
SEQuence1:EDIT:OUTCURRent 2000 //set output current limit for step No. 1 to
2000mA
| SEQuence1:EDIT:Res0.0      |     |     | //setresistanceforstepNo.1to0mΩ   |     |     |     |     |
| -------------------------- | --- | --- | --------------------------------- | --- | --- | --- | --- |
| SEQuence1:EDIT:RUNTime5    |     |     | //setrunningtimeforstepNo.1to5s   |     |     |     |     |
| SEQuence1:EDIT:LINKStart-1 |     |     | //setlinkstartstepforstepNo.1to-1 |     |     |     |     |
| SEQuence1:EDIT:LINKEnd-1   |     |     | //setlinkstopstepforstepNo.1to-1  |     |     |     |     |
| SEQuence1:EDIT:LINKCycle0  |     |     | //setlinkcycletimesto0            |     |     |     |     |
| SEQuence1:EDIT:STEP2       |     |     | //setstepNo.to2                   |     |     |     |     |
| SEQuence1:EDIT:VOLTage2.0  |     |     | //setCVValueforstepNo.2to2.0V     |     |     |     |     |
SEQuence1:EDIT:OUTCURRent 2000 //set output current limit for step No. 2 to
2000mA
| SEQuence1:EDIT:Res0.1      |     |                                              | //setresistanceforstepNo.2to0.1mΩ |     |     |     |     |
| -------------------------- | --- | -------------------------------------------- | --------------------------------- | --- | --- | --- | --- |
| SEQuence1:EDIT:RUNTime10   |     |                                              | //setrunningtimeforstepNo.2to10s  |     |     |     |     |
| SEQuence1:EDIT:LINKStart-1 |     |                                              | //setlinkstartstepforstepNo.2to-1 |     |     |     |     |
| SEQuence1:EDIT:LINKEnd-1   |     |                                              | //setlinkstopstepforstepNo.2to-1  |     |     |     |     |
| 40                         | l   |                                              |                                   |     |     |     |     |
|                            | NGI | NGI N83624SeriesProgrammingGuideSCPIProtocol |                                   |     |     |     |     |

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
SEQuence1:EDIT:LINKCycle0 //setlinkcycletimesto0
SEQuence1:EDIT:STEP3 //setstepNo.to3
SEQuence1:EDIT:VOLTage3.0 //setCVValueforstepNo.3to3.0V
SEQuence1:EDIT:OUTCURRent 2000 //set output current limit for step No. 3 to
2000mA
SEQuence1:EDIT:Res0.2 //setresistanceforstepNo.3to0.2mΩ
SEQuence1:EDIT:RUNTime20 //setrunningtimeforstepNo.3to20s
SEQuence1:EDIT:LINKStart-1 //setlinkstartstepforstepNo.3to-1
SEQuence1:EDIT:LINKEnd-1 //setlinkstopstepforstepNo.3to-1
SEQuence1:EDIT:LINKCycle0 //setlinkcycletimesto0
SEQuence1:RUN:FILE1 //settherunningSEQfileNo.to1
OUTPut1:ONOFF1 //turnontheoutputforchannel1
SEQuence1:RUN:STEP? //readthepresentrunningstepNo.
SEQuence1:RUN:T? //readrunningtimeforpresentSEQfileNo.
7.5 Measurement
There is a high-precision measurement system inside the battery simulator to
measureoutputvoltage,current,powerandtemperature.
MEASure1:CURRent? //Readthereadbackcurrentforchannel1
MEASure1:VOLTage? //Readthereadbackvoltageforchannel1
MEASure1:POWer? //Readthereal-timepowerforchannel1
MEAS2:CURR? //Readthereadbackcurrentforchannel2
MEAS2:VOLT? //Readthereadbackvoltageforchannel2
MEAS2:POW? //Readthereal-timepowerforchannel2
7.6 Factory Reset
Execute*RSTcommandtodofactoryresetonbatterysimulator.
8 Error Information
8.1 Command Error
-100 Commanderror Undefinedsyntaxerror
-101 Invalidcharacter Invalidcharacterinstring
41 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
-102 Syntaxerror Unrecognizedcommandordatatype
-103 Invalidseparator A separator is required. However the character sent
isnotaseparator.
-104 Datatypeerror Thepresentdatatypedoesnotmatchtherequiredtype.
-105 GETnotallowed The group execution trigger (GET) is received in the
programinformation.
-106 Semicolonunwanted Thereareoneormoreextrasemicolons.
-107 Commaunwanted Thereareoneormoreextracommas.
-108 Parameternotallowed The number of parameters exceeds the number
requiredbythecommand.
-109 Missingparameter The number of parameters is less than the number
required by the command, or no parameters are
inputted.
-110 Commandheadererror Undefinedcommandheadererror
-111 Headerseparatorerror A non-separator character is used in the place
oftheseparatorinthecommandheader.
-112 Programmnemonictoolong The length of mnemonic exceeds 12
characters.
-113 Undefinedheader Although the received command conforms to the
regulations in terms of syntax structure, it is not
definedinthisinstrument.
-114 Headersuffixoutofrange Thesuffixofcommandheaderisoutofrange.
-115 Commandcannotquery Thereisnoqueryformforthecommand.
-116 Commandmustquery Thecommandmustbeinqueryform.
-120 Numericdataerror Undefinednumericdataerror
-121 Invalidcharacterinnumber A data character that is not accepted by the
current command appears in the numerical
42 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
data.
-123 Exponenttoolarge Theabsolutevalueofexponentexceeds32,000.
-124 Toomanydigits Excluding the leading 0 in decimal data, the data length
exceeds255characters.
-128 Numericdatanotallowed Numerical data in the correct format is
received at a location that does not accept
numericaldata.
-130 Suffixerror Undefinedsuffixerror
-131 Invalidsuffix The suffix does not follow the syntax defined in IEEE
488.2,orthesuffixisnotsuitableforE5071C.
-134 Suffixtoolong Thesuffixislongerthan12characters.
-138 Suffixnotallowed A suffix is added to the values that are not allowed to
besuffixed.
-140 Characterdataerror Undefinedcharacterdataerror
-141 Invalidcharacterdata An invalid character was found in the
character data, or an invalid character was
received.
-144 Characterdatatoolong Thecharacterdataislongerthan12characters.
-148 Characterdatanotallowed The character data in the correct format is
received at the position where the instrument
doesnotacceptcharacterdata.
-150 Stringdataerror Undefinedstringdataerror
-151 Invalidstringdata Thestringdatathatappearsisinvalidforsomereason.
-158 Stringdatanotallowed String data is received at the position where
thisinstrumentdoesnotacceptstringdata.
-160 Blockdataerror Undefinedblockdataerror
-161 Invalidblockdata Theblockdatathatappearsisinvalidforsomereason.
43 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
-168 Blockdatanotallowed Block data is received at the position where
thisinstrumentdoesnotacceptblockdata.
-170 Expressionerror Undefinedexpressionerror
-171 Invalidexpression The expression is invalid. For example, the
bracketsarenotpairedorillegalcharactersareused.
-178 Expressiondatanotallowed Expression data is received at the position
where this instrument does not accept
expressiondata.
-180 Macroerror Undefinedmacroerror
-181 Invalidoutsidemacrodefinition There is a macro parameter
placeholder$outsidethemacrodefinition.
-183 Invalidinsidemacrodefinition There is syntax error in macro definition
(*DDT,*DMC).
-184 Macroparametererror Parameternumberorparametertypeisincorrect.
8.2 Execution Error
-200 Executionerror An error is generated that is related to execution
andcannotbedefinedbythisinstrument.
-220 Parametererror Undefinedparametererror
-221 Settingconflict The command was successfully parsed. But it can not
beexecutedduetothecurrentdevicestatus.
-222 Dataoutofrange Dataisoutofrange.
-224 Illegalparametervalue The parameter is not included in the list of
optionalparametersforthecurrentcommand.
-225 Outofmemory The available memory in this instrument is insufficient
toperformtheselectedoperation.
-232 Invalidformat Dataformatisinvalid.
-240 Hardwareerror Undefinedhardwareerror
-242 Calibrationdatalost Calibrationdataislost.
44 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol

HunanNext GenerationInstrumentalT&C Tech.Co., Ltd.
-243 NOreference Thereisnoreferencevoltage.
-256 Filenamenotfound Thefilenamecannotbefound.
-259 Notselectedfile Therearenooptionalfiles.
-295 Inputbufferoverflow Theinputbufferisoverflowing.
-296 Outputbufferoverflow Theoutputbufferisoverflowing.
45 NGI l NGI N83624SeriesProgrammingGuideSCPIProtocol
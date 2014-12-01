# PKS Muutosanalyysit - Saavutettavuus vuosina: 2009, 2013, 2017

Prosessointivaiheet saavutettavuuden muutosanalyyseihin.

## Sisältö

###2009 analyysi:

1. [Find_shortest_traveltimes_from_Logica2009data.py] (Find_shortest_traveltimes_from_Logica2009data.py) - Etsii nopeimmat matka-ajat vuoden 2009 Logica ajoista (3 eri ajankohtaa huomioitu - ajot kaikista asutuista pisteistä)
2. [Join_to_YKR_grid.py] (Join_to_YKR_grid.py) - Määrittää jokaiselle asutuspisteelle YKR-ID:n spatiaalisella joinilla MetropAccess-YKR-gridin kanssa.
3. [Aggregate_Logica2009data_by_YKRgrid.py] (Aggregate_Logica2009data_by_YKRgrid.py) - Laskee tiedot asutuspisteiden matka-ajoista (nopein / hitain / keskiarvo) kohteisiin (ostoskeskukset) aggregoiden tulokset YKR-gridiin.

###2013 analyysi:

1. [SelectDataFromTTMatrix.py] (SelectDataFromTTMatrix.py) - Määrittää matka-ajat joukkoliikenteellä ja autoillen perustuen MetropAccess-Matka-aikamatriisiin (vuosi 2013) käyttäen samoja YKR lähtö/kohdepisteitä kuin vuoden 2009 analyysissä.

###2017 analyysi:

1. [GenerateODfilesForReititin.py] (GenerateODfilesForReititin.py) - Muodostaa MetropAccess-Reitittimelle lähtöpisteet (YKR-solujen keskipisteet) ja kohdepisteet (kauppakeskusten koordinaatit) WGS84 projektiossa.
2. [run_Reititin_PKS_MuutosAnalyysi2017.bat] (run_Reititin_PKS_MuutosAnalyysi2017.bat) - Ajokomentotiedosto [Reitittimeen] (http://blogs.helsinki.fi/saavutettavuus/tyokaluja/metropaccess-reititin/) käyttäen: lähtöpisteinä [PKS_MuutosAnalyysit_OriginPoints_WGS84.txt] (ReititinFiles/PKS_MuutosAnalyysit_OriginPoints_WGS84.txt),
kohdepisteinä [PKS_MuutosAnalyysit_DestinationPoints_WGS84.txt] (ReititinFiles/PKS_MuutosAnalyysit_DestinationPoints_WGS84.txt), länsimetro+liityntälinjoina [newMetroWithFeederLines.shp] (ReititinFiles/newMetroWithFeederLines.shp),
ja parametreina [confMassaAjo.json] (ReititinFiles/confMassaAjo.json)
3. [Determine_population_projections.py] (Determine_population_projections.py) - Parsii YKR-ruutukohtaisen väestöennusteen vuodelle 2017 perustuen [Pääkaupunkiseudun väestöennusteeseen] (http://www.hri.fi/fi/dataset/paakaupunkiseudun-vaestoennuste-2012-2021)
4. [ParseReititinResults.py] (ParseReititinResults.py) - Parsii matka-ajat Reitittimen tulostiedostosta ja luo näistä YKR-gridin.

###Muutosanalyysit:

1. [Accessibility_ChangeAnalysis_years2009to2017.py] (Accessibility_ChangeAnalysis_years2009to2017.py) - Yhdistää eri vuosien datat samaan tiedostoon ja laskee ostoskeskusten saavutettavuuden ja näiden muutokset eri vuosien välillä huomioiden väestön: 2009 vs. 2013, 2009 vs. 2017, 2013 vs. 2017.






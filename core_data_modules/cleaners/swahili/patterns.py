import sys


class Patterns(object):
    """
    Lists regex patterns for cleaning Swahili demographics.
    """
    # TODO: This file is for the Swahili Demographic Cleaner, but includes regexes for English.
    male = (r'[ki]*[mwana]*ume|\b[ae]*m+[ae]le*|\bchail\b|lion|'
            r'\bchal[1l4]\b|\b(ni)*ch[ae]*[lr][eiy]*\b|'
            r'\bcharl[iy]\b|\bjali\b|\b[ae]*maie\b|\bm[ae]n\b|'
            r'\bchaliz*\b|\bbou*[iy]z*|\bbwo[iy]\b|\bgu[iy]\b|'
            r'\bdude*\b|\bbudah*\b|\bg[ae]*ntle*m[ae]n\b|'
            r'\bgentalment\b|\bm[zx]i*to*h*\b|\bkiu*me*\b|'
            r'\bja*ma+\b|\bdume*\b|\bmse\b|\bmwanaume\b|\bmwana\b|'
            r'\bsume\b|\bkijana\b|\bdaddy\b|'
            r'n*dich[uw]+o|wuo[wy]*i+|wou[wy]*i')  # luo starts here

    female = (r'\ba*f[yeai]*m[ae]*i*[kl]e*|\bfm\b|'
              r'\bm[ae]d[ae]ma*\b|\bd[ae]m[aeu]*\b|'
              r'\bch[ei]c*k*\b|\bl[ae]d[iy]\b|\bmshi*\b|'
              r'\bbmr[ae]sh\b|\bmsu*pa*\b|\bg[aiu]rl\b|'
              r'\bg[aiu]l\b|\bgyal\b|'
              r'\bm[ae][mn][jxsz][iey1l]*\b|\bmn*a*zi\b|'
              r'\bmother\b|\bmama\b|\bmwanamke\b|\bmke\b|'
              r'\bmsichana\b|\bfma*\b|\bF\b|'
              r'\b[ae]*f[yeai]*m[ae]*[kli]e*|\bki*ke*|'
              r'nya*ko|dha*ko')  # luo starts here

    one = r'moja|apei|one'
    two = r'mbili|(ng)*arei|two'
    three = r'tatu|uni|(ng)*auni|three'
    four = r'nne|ngo+mon|four'
    five = r'tano|ng[ia]\'*kan|five'
    six = r'sita|ng[ia]kanka+pei|six'
    seven = r'saba|ng[ia]kanka+rei|seven'
    eight = r'nane|ng[ia]kankauni|eight'
    nine = r'tisa|ng[ia]kanko+mwon|nine'

    # This patterns English-only because Swahili does not have this irregularity for teens.
    # Swahili represents these as "ten five".
    eleven = r'eleven'
    twelve = r'twe*lve'
    thirteen = r'thir\s*teen'
    fourteen = r'fou*r*\s*teen'
    fifteen = r'five\s*teen|fif\s*teen'
    sixteen = r'six\s*teen|sikctin'
    seventeen = r'seve*n\s*teen'
    eighteen = r'eigth*(e)*n'
    nineteen = r'nine\s*teen'

    ten = r'kumi|ng[ia]tomon|ten'
    twenty = r'ishirin[ai]|ng[ia]tomw*on arei|twenty'
    thirty = r'the[rl]athini|ng[ia]tomw*on uni|thirty'
    forty = r'arobaini|ng[ia]tomw*on omwon|fou*rty'
    fifty = r'hamsini|ng[ia]tomw*on kan|fifty'
    sixty = r'sitini|ng[ia]tomw*on kapei|sixty'
    seventy = r'sabini|ng[ia]toomw*on kaarei|seventy'
    eighty = r'themanini|ng[ia]tomw*on kauni|eighty'
    ninety = r'tisini|ng[ia]tomw*oun koomon|ninety'


class _Regex(object):
    '''
    Used to store the regexes that we use across projects. Each is stored
    in a list as the regualar expression and what it resolves to
    Edit these to your use cases
    '''

    def gender(self, gender):
        '''
        Contains gender regexes
        :param gender: string, which gender regex you'd like
        '''
        female_regex = (r'\ba*f[yeai]*m[ae]*i*[kl]e*|\bfm\b|'
                        r'\bm[ae]d[ae]ma*\b|\bd[ae]m[aeu]*\b|'
                        r'\bch[ei]c*k*\b|\bl[ae]d[iy]\b|\bmshi*\b|'
                        r'\bbmr[ae]sh\b|\bmsu*pa*\b|\bg[aiu]rl\b|'
                        r'\bg[aiu]l\b|\bgyal\b|'
                        r'\bm[ae][mn][jxsz][iey1l]*\b|\bmn*a*zi\b|'
                        r'\bmother\b|\bmama\b|\bmwanamke\b|\bmke\b|'
                        r'\bmsichana\b|\bfma*\b|\bF\b|'
                        r'\b[ae]*f[yeai]*m[ae]*[kli]e*|\bki*ke*|'
                        r'nya*ko|dha*ko')  # luo starts here
        female = [female_regex, 'female']
        male_regex = (r'[ki]*[mwana]*ume|\b[ae]*m+[ae]le*|\bchail\b|lion|'
                      r'\bchal[1l4]\b|\b(ni)*ch[ae]*[lr][eiy]*\b|'
                      r'\bcharl[iy]\b|\bjali\b|\b[ae]*maie\b|\bm[ae]n\b|'
                      r'\bchaliz*\b|\bbou*[iy]z*|\bbwo[iy]\b|\bgu[iy]\b|'
                      r'\bdude*\b|\bbudah*\b|\bg[ae]*ntle*m[ae]n\b|'
                      r'\bgentalment\b|\bm[zx]i*to*h*\b|\bkiu*me*\b|'
                      r'\bja*ma+\b|\bdume*\b|\bmse\b|\bmwanaume\b|\bmwana\b|'
                      r'\bsume\b|\bkijana\b|\bdaddy\b|'
                      r'n*dich[uw]+o|wuo[wy]*i+|wou[wy]*i')  # luo starts here
        male = [male_regex, 'male']

        gender_dict = {'f': female, 'm': male, 'female': female, 'male': male}
        if gender in gender_dict.keys():
            return gender_dict[gender]
        else:
            sys.exit('That option:{} is not available'.format(gender))

    def yes_no(self, reponse):
        '''
        Contains yes/no regexes.
        :param response: string, which response regex you'd like
        '''
        reponse = reponse.lower()
        no_regex = r'\bno\b|\bla\b|\bB\b|\b2\b|\bo+yo+\b'
        no = [no_regex, 'no']

        yes_regex = r'\byes\b|\bndiy*o\b|\bA\b|\b1\b|\b[ae]e+h*\b'
        yes = [yes_regex, 'yes']

        yes_no_dict = {'n': no, 'y': yes, 'no': no, 'yes': yes}
        if reponse in yes_no_dict.keys():
            return yes_no_dict[reponse]
        else:
            sys.exit('That option:{} is not available'.format(reponse))

    def rural_urban(self, place):
        '''
        Contains the regexes for rural/urban
        :param place: string, which place regex you'd like
        '''
        place = place.lower()
        rural_regex = (r'rural|dala|gweng|village|\bboa\b|u[sx]hag[ou]|'
                       r'u*shag[sz]')
        rural = [rural_regex, 'rural']
        urban_regex = (r'city|urban|taon|town*|taw*[ou]\b|nairobi|mjini|'
                       r'(ki)*jiji')
        urban = [urban_regex, 'urban']

        rural_urban_dict = {'rural': rural, 'urban': urban}
        if place in rural_urban_dict.keys():
            return rural_urban_dict[place]
        else:
            sys.exit('That option:{} is not available'.format(place))

    def number_word_swa(self, number):
        '''
        Contains regexes to turn words into numbers
        :param number: string, which number regex you'd like
        '''
        number = number.lower()
        one_regex = r'moja|apei|one'
        one = [one_regex, 1]
        two_regex = r'mbili|(ng)*arei|two'
        two = [two_regex, 2]
        three_regex = r'tatu|uni|(ng)*auni|three'
        three = [three_regex, 3]
        four_regex = r'nne|ngo+mon|four'
        four = [four_regex, 4]
        five_regex = r'tano|ng[ia]\'*kan|five'
        five = [five_regex, 5]
        six_regex = r'sita|ng[ia]kanka+pei|six'
        six = [six_regex, 6]
        seven_regex = r'saba|ng[ia]kanka+rei|seven'
        seven = [seven_regex, 7]
        eight_regex = r'nane|ng[ia]kankauni|eight'
        eight = [eight_regex, 8]
        nine_regex = r'tisa|ng[ia]kanko+mwon|nine'
        nine = [nine_regex, 9]

        eleven_regex = r'eleven'
        eleven = [eleven_regex, 11]
        twelve_regex = r'twe*lve'
        twelve = [twelve_regex, 12]
        thirteen_regex = r'thir\s*teen'
        thirteen = [thirteen_regex, 13]
        fourteen_regex = r'fou*r*\s*teen'
        fourteen = [fourteen_regex, 14]
        fifteen_regex = r'five\s*teen|fif\s*teen'
        fifteen = [fifteen_regex, 15]
        sixteen_regex = r'six\s*teen|sikctin'
        sixteen = [sixteen_regex, 16]
        seventeen_regex = r'seve*n\s*teen'
        seventeen = [seventeen_regex, 17]
        eighteen_regex = r'eigth*(e)*n'
        eighteen = [eighteen_regex, 18]
        nineteen_regex = r'nine\s*teen'
        nineteen = [nineteen_regex, 19]

        ten_regex = r'kumi|ng[ia]tomon|ten'
        ten = [ten_regex, 10]
        twenty_regex = r'ishirin[ai]|ng[ia]tomw*on arei|twenty'
        twenty = [twenty_regex, 20]
        thirty_regex = r'the[rl]athini|ng[ia]tomw*on uni|thirty'
        thirty = [thirty_regex, 30]
        forty_regex = r'arobaini|ng[ia]tomw*on omwon|fou*rty'
        forty = [forty_regex, 40]
        fifty_regex = r'hamsini|ng[ia]tomw*on kan|fifty'
        fifty = [fifty_regex, 50]
        sixty_regex = r'sitini|ng[ia]tomw*on kapei|sixty'
        sixty = [sixty_regex, 60]
        seventy_regex = r'sabini|ng[ia]toomw*on kaarei|seventy'
        seventy = [seventy_regex, 70]
        eighty_regex = r'themanini|ng[ia]tomw*on kauni|eighty'
        eighty = [eighty_regex, 80]
        ninety_regex = r'tisini|ng[ia]tomw*oun koomon|ninety'
        ninety = [ninety_regex, 90]

        number_dict = {'one': one, 'two': two, 'three': three, 'four': four,
                       'five': five, 'six': six, 'seven': seven,
                       'eight': eight, 'nine': nine, 'ten': ten,
                       'eleven': eleven, 'twelve': twelve,
                       'thirteen': thirteen, 'fourteen': fourteen,
                       'fifteen': fifteen, 'sixteen': sixteen,
                       'seventeen': seventeen, 'eighteen': eighteen,
                       'nineteen': nineteen, 'twenty': twenty,
                       'thirty': thirty, 'forty': forty, 'fifty': fifty,
                       'sixty': sixty, 'seventy': seventy, 'eighty': eighty,
                       'ninety': ninety}

        if number in number_dict.keys():
            return number_dict[number]
        else:
            sys.exit('That option:{} is not available'.format(number))

    def kenya_counties(self, county):
        '''
        Contains regexes to extract Kenya's conties from text
        :param county: string, which county regex you'd like
        '''
        county = county.lower()
        baringo_regex = (r'b[oae]rin[gk][0oau][cm]*|bar[aei]*ngo|bur[yi]+a|'
                         r'elda[mr]a|kab[ae]rnet|kab[ae]rtonjo|kabiyamoto|'
                         r'koiba*te*k|koibaraka|mogotio|ravin')
        baringo = [baringo_regex, 'Baringo']
        bomet_regex = r'b[aou]*m[ae]*t|b[on]men?t|sotik'
        bomet = [bomet_regex, 'Bomet']
        bungoma_regex = (r'\s\S*\sn\sg\so\sm\sa|bung\so\sm\sa|'
                         r'm?[bp][iauo][nm]gom[aeious]|bug[no][no]m[as]|'
                         r'bukoma|bumula|bungo[nw]a|bun[gkq]om[as]|kand[uyi]*|'
                         r'kim(il)?ili|webuye')
        bungoma = [bungoma_regex, 'Bungoma']
        busia_regex = (r'bu[sxc]i?a*|b[aeio][sxc][ei]?[aeo]|budalang\S*i|'
                       r'bu(si)+a|butula|makuyu|malaba|namable|teso')
        busia = [busia_regex, 'Busia']
        embu_regex = (r'e\s*m\s*b\s*[uo]\s*|emb[uo]h|kianjokoma|mbe*re|'
                      r'runyenjes|\b[aei]mb[ou]*\b|\bebu\b')
        embu = [embu_regex, 'Embu']
        garissa_regex = r'gar+is+a*|\bgj\b|\bn?g[ae]*r+[ei]ss*[ae]*\b'
        garissa = [garissa_regex, 'Garissa']
        homabay_regex = (r'h?[o0a]m+[ay][ay]?\s?([bp][ae][yi])?|'
                         r'\bh[\-\.\_]?b([ea]y)?\b|(ka)?rachuonyo|mbita|'
                         r'h?[o0a]m+[ae]?[\-\.\_]?a?[bp][ae][yi]|h[o0a]m+a\b'
                         r'oyugis|ringa')
        homabay = [homabay_regex, 'Homa-Bay']
        isiolo_regex = r'i[sx]sio[lr]o|\b[aei][sx][eiy]*[aou]l[aou]*\b'
        isiolo = [isiolo_regex, 'Isiolo']
        kajiado_regex = (r'i[sx]inya|k[ai]*[(ch)jn]*[iu]*a[dh]?a?o|kgjiado|'
                         r'kise(rian?)?|kitenge[l]a|\bkjd\b|loito?ki?tok|'
                         r'matasia|(na)?manga|oledoinyo|olekejuado|olepolos|'
                         r'oloitokto|ongat+a|\s*ron?gai?|qajadoh\b|'
                         r'\bk[ai]*n*[jg][aei][aei]*n*[oa]*d[ou]*')
        kajiado = [kajiado_regex, 'Kajiado']
        kakamega_regex = (r'bukhungu|bunyore|butere|eshikulusi|\s*kame\s*|'
                          r'\bk\.?m\.?g\.?\b|kabras|kat?[(ch)(mega)]|khwisero|'
                          r'likuyani|lugari|lurambi|madunta|malava|manyulia|'
                          r'k[ea][(ch)gk][\siae]?me(nh)?[gqk]a\b|mumias|'
                          r'navakholo|sokomoko|gagamega')
        kakamega = [kakamega_regex, 'Kakamega']
        kericho_regex = r'[kq][aeiou]*r[aei]*[csjx]?h?[o0u]*h?|bureti|londiani'
        kericho = [kericho_regex, 'Kericho']
        kiambu_regex = (r'ga2du|gachie|gatan?ga|g[ae]th[uo]*rai|'
                        r'[gk][ai](tu)?kuyu|[gk][ei]thu(ngu)?[lr]a?i|gatundu|'
                        r'[kq][i1ae]?[ae]w?[mb][mb]*[uo]|kaimbu(jah)?|kabete|'
                        r'kamwangi|\bkiam\sb\su\b|k\si\sa\sm\sb\su\s*|'
                        r'ki+a[mn]b?([au]+[pi]?)?|kwyabu|\blari\b|makogenu|'
                        r'\bmangu\b|ruaka|ruiru|thi*ka*|thome|wangig[ie]|'
                        r'\bl[ie]*m[ou]*r[ou]*\b')
        kiambu = [kiambu_regex, 'Kiambu']
        kilifi_regex = (r'k[aei]l[ie](f[ph])[iky]|mali?nd[ei]?|maqarini|'
                        r'mariakani|mitangoni|mtwapa')
        kilifi = [kilifi_regex, 'Kilifi']
        kirinyaga_regex = (r'kabare|kagio|kagumo|k[aei]r[aei]nyan?g\S?a|'
                           r'ker[uo]n?(goya)?|kil?[ia]*n?yaga|kimbaby|'
                           r'kip?r+[ia]n?[yg]?an?ga|kirnygh|kisasi|kutus|'
                           r'maktuno|sagana|mwea|kirinya|kariayanga|'
                           r'\bk[aeiy]*r[yiou]*n*[iy][aei]*g[ae]*\b')
        kirinyaga = [kirinyaga_regex, 'Kirinyaga']
        kisii_regex = (r'm?k\s*i\s*[sc]\s*i\s*i*l?|ks?i+[scxz]*[eil]*|'
                       r'nyaribari|maxaba|ogembo')
        kisii = [kisii_regex, 'Kisii']
        kisumu_regex = (r'k+\S?s*u[mn][iu]|isumu|k\si\ss\su\sm\su|kondele|'
                        r'Luanda|muhoroni|nikisumu|nyadal|seme|'
                        r'\bk[aeiou]*[szx][aeiou]*[mw][aeiou]*')
        kisumu = [kisumu_regex, 'Kisumu']
        kitui_regex = (r'[cqk]u?[iy]?[t2]?[wou]?\s*[yeli]i?|kabati|katheuni|'
                       r'katulani|kavisuni|mwi?ng(wan)?[ji]')
        kitui = [kitui_regex, 'Kitui']
        kwale_regex = (r'diani|hamisi|kinango|k[wu]a[l][aei]|lunga|mangweni|'
                       r'msambweni*|ukunda|undanyi')
        kwale = [kwale_regex, 'Kwale']
        laikipia_regex = (r'gatundia|kglakipia|laikip[il]aik[gi]p[iy]|'
                          r'laikip?a*\b|\blac\s?(nyu)?\b|nan?yukie?|'
                          r'nyah[eiu]([l]u)*|nyanyuki|nyaururu|rumuruti|'
                          r'\bl[ae]*[yei]*k[yeil]*p[yei][ae]*\b|\blaki\b|'
                          r'laikikipia')
        laikipia = [laikipia_regex, 'Laikipia']
        lamu_regex = r'\blam\b|lam[ou]'
        lamu = [lamu_regex, 'Lamu']
        machakos_regex = (r'kangundo|katangi|kathiani|kilima|kiva+|mac?h[ao]*|'
                          r'ma[(ch)x]?[aeo][xk][ou]r?s?|majacoz|masku|masinga|'
                          r'ma[sc]ha[ck]o?e?[zxs]?|matungulu|matu+|mavoko|'
                          r'maxh?akos|ml?olongo|\btala\b|\bmcha\b|a+thi+')
        machakos = [machakos_regex, 'Machakos']
        makueni_regex = (r'kathonzweni|kibwezi|kisau|'
                         r'm[au]?[kq][uw]*[aei]?n[yhi]?e*|makindu|mak(tu)?eni|'
                         r'makui|ma[q(ku)]wen|mtito|mukui')
        makueni = [makueni_regex, 'Makueni']
        mandera_regex = r'man?de[l]a|\bm[aei]*n*d[aei]*r[ae]*\b'
        mandera = [mandera_regex, 'Mandera']
        marakwet_regex = (r'el?[gk][ei]*yo|elg[aeiou]*|ite[mn]|maran?gwet|'
                          r'ma*r[aeiou]*kw[aei]*t|[kg]eiyo')
        marakwet = [marakwet_regex, 'Marakwet']
        marsabit_regex = (r'mar?[sx]abit|\bm[aei]*rs[aei]*b[aei]*t\b|moyale|'
                          r'marsabit')
        marsabit = [marsabit_regex, 'Marsabit']
        meru_regex = (r'm\s*[ea]\s*r\s*[ouy]|m[ae]r[ouy]|imenti\b|bu+ri|'
                      r'[ei]gembe|giaki|igoj?i|iment\S*\s*|maua|nkubu|tigania|'
                      r'tima?u|nikomeru|meruc')
        meru = [meru_regex, 'Meru']
        migori_regex = (r'mi?n?go?[l]i?|migingo|nyasare|nyatike|'
                        r'\bmig[aeio]*r[yiou]*\b')
        migori = [migori_regex, 'Migori']
        mombasa_regex = (r'bamburi|changamwe|hamisa|kilindn|likoni|mawen|'
                         r'mazeras|\bmbs\b|\bmsa\b|mikindani|mombasani|'
                         r'mw?[o0]?m?ba[xs7c(th)]*[ao]?|'
                         r'\bm[aou]*m*b[aeo]*ss*[ae]*\b')
        mombasa = [mombasa_regex, 'Mombasa']
        muranga_regex = (r'githiga|kahuhia|kan[dg]ara|kang[ae]m[ea]|\bmuran\b|'
                         r'mai?th(io)*ya|ma[lr]g[uw]a|marangwa|muthith?i|'
                         r'm[au]?\S?[l]a\S?n\S?g\S?a|mun?r\S?\s?r?an?g?a|'
                         r'm\s?u\s?r\s?\s?a\s?n\s?g\s?a|sabasaba|'
                         r'\bm[ou]*[lr][aeiou]*[mn]*g\'*[ae]*\b')
        muranga = [muranga_regex, 'Muranga']
        nairobi_regex = (r'babandogo|(buru)+|dag+or*[aei]?t*i*|esili|\bhamz\b|'
                         r'do[hn][hn]h?ol?m|eaxleigh|em?ba([ckj]a[scx]+[yi])?|'
                         r'estlighet|g[ei]thurai|'
                         r'isli|kahawa|kam[kl]u(nji)?|kangemi|karen|kikomba|'
                         r'kasha|kawan?gwa[g]e|kayole|kib[ei]?ra|'
                         r'komarock|korogocho|lang\S?ata|lavington|makadara|'
                         r'dand([ao]r)?[ao]|huruma|'
                         r'mwiki|9r?bi?|'
                         r'nar[io][io]*bi|\bnrb\b|nairnb|ngala|ngong|njiru'
                         r'ro[iy]samb[ou]|rongai|ruw?ai|'
                         r'ruaraka|[xs]tarehe|umoja|utawala|ungwaro|'
                         r'[sx]outh\s?[bc]|kariobangi|kasarani|pipeline4|'
                         r'nyayo|westlands*|westi|nai+(ro)?')
        nairobi = [nairobi_regex, 'Nairobi']
        nakuru_regex = (r'bahati|elburgon|gil\s?gil|karagita|kiambogo|nakurt|'
                        r'maai\s?mahiu|\bmau\b|mawanga|molo|kiamnyeki|nskuru|'
                        r'n\s?a\s?k\s?u\s?r\s?[iou]\s?|nai?[qgk][au]ru+|'
                        r'na[ckq]r?[sxz]?(\s?vegas)?|na[x][ks][sx]?|'
                        r'nak[cia]?s?|nak+u+r+u+|nak[sx]\s?vegas|sum?bukia|'
                        r'naku[lrs]u[ck]?u?|naku[lr]o?[zk]?a|nu?k[sx]|'
                        r'rift\s?valley')
        nakuru = [nakuru_regex, 'Nakuru']
        nandi_regex = r'emgwen|kap[sx]a[brp][ei]t|mosop|n[ae]n?d[iely]+'
        nandi = [nandi_regex, 'Nandi']
        narok_regex = (r'ma+[s]ai*|mulot|naro?([cr]?ko?)?|na[lr]ok|olerai|'
                       r'\bnar[aeiou]*k\b')
        narok = [narok_regex, 'Narok']
        nyamira_regex = (r'keroka|ny[a@]?[mi1][mi1]?[lr][a@]?|'
                         r'\bn[yi]*am[aeiou]*ra*\b')
        nyamira = [nyamira_regex, 'Nyamira']
        nyandarua_regex = (r'kinan?gop|kiritiri|nyambura|magum|nyanxa|nydrua|'
                           r'(ol)?e?\s?kal[ao][ou]|waithaka|wanjohi|'
                           r'\bn[yi]an*d[ae]r[wou]*[ae]*\b|'
                           r's?nyan?da[lr][au]w?[au]a?')
        nyandarua = [nyandarua_regex, 'Nyandarua']
        nyeri_regex = (r'karatina|kieni|mat?hi[gr]a|muku[lr]we\S?\s?i?ni|'
                       r'[mn]yeri|[mn][ye]\S?[ye]r[ij]|na[l][ou]mo[lr]u|'
                       r'othaya|tetu|ruringu|\bn[yi][aei]*[l][yi]*\b')
        nyeri = [nyeri_regex, 'Nyeri']
        samburu_regex = (r'mara[gl][ao]lwamba|\bs[ae]*m*b[ou]*r[ou]*\b|'
                         r'barag[ow]i')
        samburu = [samburu_regex, 'Samburu']
        siaya_regex = (r'bondo|ciaya|\bgem\b|nyanza|rarieda|ug[eu]n[jy]a|'
                       r'[sx][ai][ai]ya(ia)?|\bs[iy]a[yi]a*\b|siyaya')
        siaya = [siaya_regex, 'Siaya']
        taita_taveta_regex = (r'kimonge|maungu|mwatate|taita(\S?\s?taves?ta)?|'
                              r'\btvt\b|\btz\b|\bvoi\b|\bt[ae]*[yi]t[ae]*\b|'
                              r'tsavesta|\bt[ae]*v[aei]t[aeiou]*\b')
        taita_taveta = [taita_taveta_regex, 'Taita-Taveta']
        tana_river_regex = r'\btan[ae]*\S*\s*ri*v[ae]*r*\b|garsen'
        tana_river = [tana_river_regex, 'Tana-River']
        tharaka_nithi_regex = (r'th*[ae]*[lr]aka*n?\S*\s*n(i?th?[yi])?(dh)?|'
                               r'n?thakanthi|dharaka\S*\s*(nthi)?|chu[kx]*a*|'
                               r'ch[o0]g[o0]ria')
        tharaka_nithi = [tharaka_nithi_regex, 'Tharaka-Nithi']
        trans_nzoia_regex = (r'nozia|tu?ra?[nz][nz]?(o?ya?)?h?|endebess|'
                             r'tra[nz][nz]([io][aio]?[iy]?a?)?|kachibora|'
                             r'([dt]r)?a?n?[sxz]*[\-\_\.\/\s]*(n?[sz])?o[iy1\s]*[ao]h?|'
                             r'bondeni|cherengan[iy]*|kiminini|mitume|saboti|'
                             r'kital[ae](le)?|\btu?[i1l]\b|kibomet')
        trans_nzoia = [trans_nzoia_regex, 'Trans-Nzoia']
        turkana_regex = (r'[t2]r?[aou]*r*u?[ck][aeiou]*n[aeiou]*|turkland|'
                         r'\blo*dwar*\b|lo[ck]ichog+[iey]o|naoros|ka?kum+a')
        turkana = [turkana_regex, 'Turkana']
        uasin_gishu_regex = (r'chepkoliel|eld?[no]?[lr][ae]te*|\bld\b|'
                             r'e[dl]d?[no]?[lr][ae]te?|e\.?l\.?d\.?y?|'
                             r'matunda|moisbr[i1]?dge|moiben|turbo|langas?|'
                             r'uas[ah]?in?\s*g[iu]?[sc]h[iu]|uas?n\s?gish|'
                             r'usigi\s*shu|\bu\.?g\.?\b|wareng|wapi|'
                             r'\b[wu][aeiou]n*[szx][aeiou][mn]*|'
                             r'g[aeiou][(sh)x]h*u\b|eld[oe]ret*|wasigishu|'
                             r'uasingi[xs]h8u|ushu\s?gizu|ugsigshu|'
                             r'el[ai]d?o[lr][ae]te?|usa?in(\s?ghisue)?|')
        uasin_gishu = [uasin_gishu_regex, 'Uasin-Gishu']
        vihiga_regex = (r'emuhaya|fihinga|hamisi|kaimosi|sabatia|'
                        r'[uv]\s?[1il]\s?h?\s?[e1iln]\s?g+\s?[ae]?|'
                        r'\bv\.?h\.?g\.?a?\.?\b|vini\s?bg|\bv[hi]?ga\b')
        vihiga = [vihiga_regex, 'Vihiga']
        wajir_regex = r'\bw[ae][jg][iy]r*\b|\bwaijia\b'
        wajir = [wajir_regex, 'Wajir']
        west_pokot_regex = r'\bpo?k[aeiou]*t\b|\bkape(n?guria)?\b'
        west_pokot = [west_pokot_regex, 'West-Pokot']

        county_dict = {'baringo': baringo, 'bomet': bomet, 'bungoma': bungoma,
                       'busia': busia, 'embu': embu, 'garissa': garissa,
                       'homabay': homabay, 'isiolo': isiolo,
                       'kajiado': kajiado, 'kakamega': kakamega,
                       'kericho': kericho, 'kiambu': kiambu, 'kilifi': kilifi,
                       'kirinyaga': kirinyaga, 'kisii': kisii,
                       'kisumu': kisumu, 'kitui': kitui, 'kwale': kwale,
                       'laikipia': laikipia, 'lamu': lamu,
                       'machakos': machakos, 'makueni': makueni,
                       'mandera': mandera, 'marakwet': marakwet,
                       'marsabit': marsabit, 'meru': meru, 'migori': migori,
                       'mombasa': mombasa, 'muranga': muranga,
                       'nairobi': nairobi, 'nakuru': nakuru, 'nandi': nandi,
                       'narok': narok, 'nyamira': nyamira,
                       'nyandarua': nyandarua, 'nyeri': nyeri,
                       'samburu': samburu, 'siaya': siaya,
                       'taita_taveta': taita_taveta, 'taita': taita_taveta,
                       'taveta': taita_taveta, 'tana_river': tana_river,
                       'tana': tana_river, 'tharaka_nithi': tharaka_nithi,
                       'trans_nzoia': trans_nzoia, 'nzoia': trans_nzoia,
                       'turkana': turkana, 'uasin_gishu': uasin_gishu,
                       'vihiga': vihiga, 'wajir': wajir,
                       'west_pokot': west_pokot, 'pokot': west_pokot}

        if county in county_dict.keys():
            return county_dict[county]
        else:
            sys.exit('That option:{} is not available'.format(county))

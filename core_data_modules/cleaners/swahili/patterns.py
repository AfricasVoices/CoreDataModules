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

push FLAGS="-u" BRANSH="aurora":
    git push {{FLAGS}} origin {{BRANSH}} 
    git push {{FLAGS}} gitlab {{BRANSH}} 
    git push {{FLAGS}} codeberg {{BRANSH}} 
    git push {{FLAGS}} disroot {{BRANSH}} 

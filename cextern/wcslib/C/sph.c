/*============================================================================
  WCSLIB 8.4 - an implementation of the FITS WCS standard.
  Copyright (C) 1995-2024, Mark Calabretta

  This file is part of WCSLIB.

  WCSLIB is free software: you can redistribute it and/or modify it under the
  terms of the GNU Lesser General Public License as published by the Free
  Software Foundation, either version 3 of the License, or (at your option)
  any later version.

  WCSLIB is distributed in the hope that it will be useful, but WITHOUT ANY
  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
  FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for
  more details.

  You should have received a copy of the GNU Lesser General Public License
  along with WCSLIB.  If not, see http://www.gnu.org/licenses.

  Author: Mark Calabretta, Australia Telescope National Facility, CSIRO.
  http://www.atnf.csiro.au/people/Mark.Calabretta
  $Id: sph.c,v 8.4 2024/10/28 13:56:16 mcalabre Exp $
*===========================================================================*/

#include <math.h>
#include "wcstrig.h"
#include "sph.h"

#define copysign(X, Y) ((Y) < 0.0 ? -fabs(X) : fabs(X))

#define tol 1.0e-5

//----------------------------------------------------------------------------

int sphx2s(
  const double eul[5],
  int nphi,
  int ntheta,
  int spt,
  int sll,
  const double phi[],
  const double theta[],
  double lng[],
  double lat[])

{
  int mphi, mtheta;
  if (ntheta > 0) {
    mphi   = nphi;
    mtheta = ntheta;
  } else {
    mphi   = 1;
    mtheta = 1;
    ntheta = nphi;
  }


  // Check for special-case rotations.
  if (eul[4] == 0.0) {
    if (eul[1] == 0.0) {
      // Simple change in origin of longitude.
      double dlng = fmod(eul[0] + 180.0 - eul[2], 360.0);

      int jphi = 0;
      const double *thetap = theta;
      double *lngp   = lng;
      double *latp   = lat;
      for (int itheta = 0; itheta < ntheta; itheta++, thetap += spt) {
        const double *phip = phi + (jphi%nphi)*spt;
        for (int iphi = 0; iphi < mphi; iphi++, phip += spt, jphi++) {
          *lngp = *phip + dlng;
          *latp = *thetap;

          // Normalize the celestial longitude.
          if (eul[0] >= 0.0) {
            if (*lngp < 0.0) *lngp += 360.0;
          } else {
            if (*lngp > 0.0) *lngp -= 360.0;
          }

          if (*lngp > 360.0) {
            *lngp -= 360.0;
          } else if (*lngp < -360.0) {
            *lngp += 360.0;
          }

          lngp += sll;
          latp += sll;
        }
      }

    } else {
      // Pole-flip with change in origin of longitude.
      double dlng = fmod(eul[0] + eul[2], 360.0);

      int jphi = 0;
      const double *thetap = theta;
      double *lngp   = lng;
      double *latp   = lat;
      for (int itheta = 0; itheta < ntheta; itheta++, thetap += spt) {
        const double *phip = phi + (jphi%nphi)*spt;
        for (int iphi = 0; iphi < mphi; iphi++, phip += spt, jphi++) {
          *lngp = dlng - *phip;
          *latp = -(*thetap);

          // Normalize the celestial longitude.
          if (eul[0] >= 0.0) {
            if (*lngp < 0.0) *lngp += 360.0;
          } else {
            if (*lngp > 0.0) *lngp -= 360.0;
          }

          if (*lngp > 360.0) {
            *lngp -= 360.0;
          } else if (*lngp < -360.0) {
            *lngp += 360.0;
          }

          lngp += sll;
          latp += sll;
        }
      }
    }

    return 0;
  }


  // Do phi dependency.
  const double *phip = phi;
  int rowoff = 0;
  int rowlen = nphi*sll;
  for (int iphi = 0; iphi < nphi; iphi++, rowoff += sll, phip += spt) {
    double dphi = *phip - eul[2];

    double *lngp = lng + rowoff;
    for (int itheta = 0; itheta < mtheta; itheta++) {
      *lngp = dphi;
      lngp += rowlen;
    }
  }


  // Do theta dependency.
  const double *thetap = theta;
  double *lngp = lng;
  double *latp = lat;
  for (int itheta = 0; itheta < ntheta; itheta++, thetap += spt) {
    double sinthe, costhe;
    sincosd(*thetap, &sinthe, &costhe);

    double costhe3 = costhe*eul[3];
    double costhe4 = costhe*eul[4];
    double sinthe3 = sinthe*eul[3];
    double sinthe4 = sinthe*eul[4];

    for (int iphi = 0; iphi < mphi; iphi++, lngp += sll, latp += sll) {
      double dphi = *lngp;
      double sinphi, cosphi;
      sincosd(dphi, &sinphi, &cosphi);

      // Compute the celestial longitude.
      double x = sinthe4 - costhe3*cosphi;
      if (fabs(x) < tol) {
        // Rearrange formula to reduce roundoff errors.
        x = -cosd(*thetap + eul[1]) + costhe3*(1.0 - cosphi);
      }

      double dlng;
      double y = -costhe*sinphi;
      if (x != 0.0 || y != 0.0) {
        dlng = atan2d(y, x);
      } else {
        // Change of origin of longitude.
        if (eul[1] < 90.0) {
          dlng =  dphi + 180.0;
        } else {
          dlng = -dphi;
        }
      }
      *lngp = eul[0] + dlng;

      // Normalize the celestial longitude.
      if (eul[0] >= 0.0) {
        if (*lngp < 0.0) *lngp += 360.0;
      } else {
        if (*lngp > 0.0) *lngp -= 360.0;
      }

      if (*lngp > 360.0) {
        *lngp -= 360.0;
      } else if (*lngp < -360.0) {
        *lngp += 360.0;
      }

      // Compute the celestial latitude.
      if (fmod(dphi,180.0) == 0.0) {
        *latp = *thetap + cosphi*eul[1];
        if (*latp >  90.0) *latp =  180.0 - *latp;
        if (*latp < -90.0) *latp = -180.0 - *latp;
      } else {
        double z = sinthe3 + costhe4*cosphi;
        if (fabs(z) > 0.99) {
          // Use an alternative formula for greater accuracy.
          *latp = copysign(acosd(sqrt(x*x+y*y)), z);
        } else {
          *latp = asind(z);
        }
      }
    }
  }

  return 0;
}

//----------------------------------------------------------------------------

int sphs2x(
  const double eul[5],
  int nlng,
  int nlat,
  int sll,
  int spt,
  const double lng[],
  const double lat[],
  double phi[],
  double theta[])

{
  int mlng, mlat;
  if (nlat > 0) {
    mlng = nlng;
    mlat = nlat;
  } else {
    mlng = 1;
    mlat = 1;
    nlat = nlng;
  }


  // Check for special-case rotations.
  if (eul[4] == 0.0) {
    if (eul[1] == 0.0) {
      // Simple change in origin of longitude.
      double dphi = fmod(eul[2] - 180.0 - eul[0], 360.0);

      int jlng = 0;
      const double *latp   = lat;
      double *phip   = phi;
      double *thetap = theta;
      for (int ilat = 0; ilat < nlat; ilat++, latp += sll) {
        const double *lngp = lng + (jlng%nlng)*sll;
        for (int ilng = 0; ilng < mlng; ilng++, lngp += sll, jlng++) {
          *phip = fmod(*lngp + dphi, 360.0);
          *thetap = *latp;

          // Normalize the native longitude.
          if (*phip > 180.0) {
            *phip -= 360.0;
          } else if (*phip < -180.0) {
            *phip += 360.0;
          }

          phip   += spt;
          thetap += spt;
        }
      }

    } else {
      // Pole-flip with change in origin of longitude.
      double dphi = fmod(eul[2] + eul[0], 360.0);

      int jlng   = 0;
      const double *latp   = lat;
      double *phip   = phi;
      double *thetap = theta;
      for (int ilat = 0; ilat < nlat; ilat++, latp += sll) {
        const double *lngp = lng + (jlng%nlng)*sll;
        for (int ilng = 0; ilng < mlng; ilng++, lngp += sll, jlng++) {
          *phip = fmod(dphi - *lngp, 360.0);
          *thetap = -(*latp);

          // Normalize the native longitude.
          if (*phip > 180.0) {
            *phip -= 360.0;
          } else if (*phip < -180.0) {
            *phip += 360.0;
          }

          phip   += spt;
          thetap += spt;
        }
      }
    }

    return 0;
  }


  // Do lng dependency.
  const double *lngp = lng;
  int rowoff = 0;
  int rowlen = nlng*spt;
  for (int ilng = 0; ilng < nlng; ilng++, rowoff += spt, lngp += sll) {
    double dlng = *lngp - eul[0];

    double *phip = phi + rowoff;
    for (int ilat = 0; ilat < mlat; ilat++) {
      *phip = dlng;
      phip += rowlen;
    }
  }


  // Do lat dependency.
  const double *latp = lat;
  double *phip   = phi;
  double *thetap = theta;
  for (int ilat = 0; ilat < nlat; ilat++, latp += sll) {
    double sinlat, coslat;
    sincosd(*latp, &sinlat, &coslat);

    double coslat3 = coslat*eul[3];
    double coslat4 = coslat*eul[4];
    double sinlat3 = sinlat*eul[3];
    double sinlat4 = sinlat*eul[4];

    for (int ilng = 0; ilng < mlng; ilng++, phip += spt, thetap += spt) {
      double dlng = *phip;
      double sinlng, coslng;
      sincosd(dlng, &sinlng, &coslng);

      // Compute the native longitude.
      double x = sinlat4 - coslat3*coslng;
      if (fabs(x) < tol) {
        // Rearrange formula to reduce roundoff errors.
        x = -cosd(*latp+eul[1]) + coslat3*(1.0 - coslng);
      }

      double dphi;
      double y = -coslat*sinlng;
      if (x != 0.0 || y != 0.0) {
        dphi = atan2d(y, x);
      } else {
        // Change of origin of longitude.
        if (eul[1] < 90.0) {
          dphi =  dlng - 180.0;
        } else {
          dphi = -dlng;
        }
      }
      *phip = fmod(eul[2] + dphi, 360.0);

      // Normalize the native longitude.
      if (*phip > 180.0) {
        *phip -= 360.0;
      } else if (*phip < -180.0) {
        *phip += 360.0;
      }

      // Compute the native latitude.
      if (fmod(dlng,180.0) == 0.0) {
        *thetap = *latp + coslng*eul[1];
        if (*thetap >  90.0) *thetap =  180.0 - *thetap;
        if (*thetap < -90.0) *thetap = -180.0 - *thetap;
      } else {
        double z = sinlat3 + coslat4*coslng;
        if (fabs(z) > 0.99) {
          // Use an alternative formula for greater accuracy.
          *thetap = copysign(acosd(sqrt(x*x+y*y)), z);
        } else {
          *thetap = asind(z);
        }
      }
    }
  }

  return 0;
}

//----------------------------------------------------------------------------

int sphdpa(
  int nfield,
  double lng0,
  double lat0,
  const double lng[],
  const double lat[],
  double dist[],
  double pa[])

{
  // Set the Euler angles for the coordinate transformation.
  double eul[5];
  eul[0] = lng0;
  eul[1] = 90.0 - lat0;
  eul[2] = 0.0;
  eul[3] = cosd(eul[1]);
  eul[4] = sind(eul[1]);

  // Transform field points to the new system.
  sphs2x(eul, nfield, 0, 1, 1, lng, lat, pa, dist);

  for (int i = 0; i < nfield; i++) {
    // Angular distance is obtained from latitude in the new frame.
    dist[i] = 90.0 - dist[i];

    // Position angle is obtained from longitude in the new frame.
    pa[i] = -pa[i];
    if (pa[i] < -180.0) pa[i] += 360.0;
  }

  return 0;
}

//----------------------------------------------------------------------------

int sphpad(
  int nfield,
  double lng0,
  double lat0,
  const double dist[],
  const double pa[],
  double lng[],
  double lat[])

{
  // Set the Euler angles for the coordinate transformation.
  double eul[5];
  eul[0] = lng0;
  eul[1] = 90.0 - lat0;
  eul[2] = 0.0;
  eul[3] = cosd(eul[1]);
  eul[4] = sind(eul[1]);

  for (int i = 0; i < nfield; i++) {
    // Latitude in the new frame is obtained from angular distance.
    lat[i] = 90.0 - dist[i];

    // Longitude in the new frame is obtained from position angle.
    lng[i] = -pa[i];
  }

  // Transform field points to the old system.
  sphx2s(eul, nfield, 0, 1, 1, lng, lat, lng, lat);

  return 0;
}

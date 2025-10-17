import React from 'react';
import { Card, CardContent, CardHeader } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { MapPin, Calendar, Mail, Phone, Edit3 } from 'lucide-react';
import UserAvatar from './UserAvatar';

interface ProfileCardProps {
  user: {
    name: string;
    avatar?: string;
    email?: string;
    phone?: string;
    location?: string;
    joinDate?: string;
    bio?: string;
    badges?: string[];
    isOwnProfile?: boolean;
  };
  onEdit?: () => void;
  onFollow?: () => void;
  className?: string;
}

const ProfileCard: React.FC<ProfileCardProps> = ({
  user,
  onEdit,
  onFollow,
  className
}) => {
  const {
    name,
    avatar,
    email,
    phone,
    location,
    joinDate,
    bio,
    badges = [],
    isOwnProfile = false
  } = user;

  return (
    <Card className={className}>
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-4">
            <UserAvatar
              src={avatar}
              name={name}
              size="lg"
              className="flex-shrink-0"
            />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">{name}</h2>
              {location && (
                <div className="flex items-center text-sm text-gray-500 mt-1">
                  <MapPin className="h-4 w-4 mr-1" />
                  {location}
                </div>
              )}
              {joinDate && (
                <div className="flex items-center text-sm text-gray-500 mt-1">
                  <Calendar className="h-4 w-4 mr-1" />
                  加入于 {joinDate}
                </div>
              )}
            </div>
          </div>
          
          <div className="flex flex-col space-y-2">
            {isOwnProfile ? (
              <Button onClick={onEdit} size="sm" variant="outline">
                <Edit3 className="h-4 w-4 mr-2" />
                编辑资料
              </Button>
            ) : (
              <Button onClick={onFollow} size="sm">
                关注
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Bio */}
        {bio && (
          <div>
            <p className="text-gray-700 leading-relaxed">{bio}</p>
          </div>
        )}

        {/* Badges */}
        {badges.length > 0 && (
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-2">标签</h3>
            <div className="flex flex-wrap gap-2">
              {badges.map((badge, index) => (
                <Badge key={index} variant="secondary">
                  {badge}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Contact Info */}
        <div className="space-y-2 pt-4 border-t">
          {email && (
            <div className="flex items-center text-sm text-gray-600">
              <Mail className="h-4 w-4 mr-2" />
              {email}
            </div>
          )}
          {phone && (
            <div className="flex items-center text-sm text-gray-600">
              <Phone className="h-4 w-4 mr-2" />
              {phone}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ProfileCard;

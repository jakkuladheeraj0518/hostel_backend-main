    def create(self, user_data: UserCreate) -> User:
        """Create new user"""
        hashed_password = None
        if user_data.password:
            hashed_password = get_password_hash(user_data.password)
        # Normalize hostel_id: treat 0 or other falsy values as None to avoid FK violations
        raw_hostel_id = getattr(user_data, 'hostel_id', None)
        try:
            hostel_id = int(raw_hostel_id) if raw_hostel_id is not None else None
            if hostel_id is not None and hostel_id <= 0:
                hostel_id = None
        except Exception:
            hostel_id = None

        # Ensure 'name' is populated since it's nullable=False in the DB model
        # Use full_name if available, else fallback to username
        user_name_val = user_data.full_name or user_data.username

        db_user = User(
            email=user_data.email,
            phone_number=getattr(user_data, 'phone_number', None),
            country_code=getattr(user_data, 'country_code', None),
            username=user_data.username,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            name=user_name_val,  # FIX: Explicitly set the required 'name' field
            role=user_data.role,
            hostel_id=hostel_id,
            is_active=getattr(user_data, 'is_active', False) # Default to False if not specified, logic handles auto-activation
        )
        self.db.add(db_user)
        try:
            self.db.commit()
            self.db.refresh(db_user)
        except Exception:
            # surface a clearer error for foreign-key/constraint issues
            self.db.rollback()
            raise
        return db_user